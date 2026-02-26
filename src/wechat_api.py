#!/usr/bin/env python3
"""
微信公众号 API 封装模块
处理 Access Token 管理、素材上传、草稿管理等
"""

import time
import random
import requests
from functools import wraps
from typing import Optional, Dict, List, BinaryIO
from src.config import config


def retry_on_error(max_retries: int = 3, backoff_factor: float = 1.0, 
                   retryable_errors: tuple = (40001, 42001, 45009)):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子（每次重试等待时间 = backoff_factor * (2 ** retry_count)）
        retryable_errors: 需要重试的错误码（默认为 Token 过期、系统繁忙等）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for retry_count in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except WeChatAPIError as e:
                    last_exception = e
                    
                    # 检查是否需要重试
                    if e.errcode in retryable_errors and retry_count < max_retries:
                        # 指数退避 + 随机抖动
                        wait_time = backoff_factor * (2 ** retry_count) + random.uniform(0, 0.5)
                        print(f"   [RETRY] 请求失败 ({e.errcode}: {e.errmsg})，{wait_time:.1f}秒后重试 ({retry_count + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        
                        # 如果是 Token 过期错误，刷新 Token
                        if e.errcode == 40001:
                            # 获取 self（如果是类方法）
                            if args and hasattr(args[0], 'token_manager'):
                                args[0].token_manager.clear_cache()
                                print("   [RETRY] Token 已刷新")
                    else:
                        # 不需要重试的错误，直接抛出
                        raise
            
            # 重试次数用尽
            raise last_exception
        return wrapper
    return decorator


class WeChatAPIError(Exception):
    """微信 API 错误"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"WeChat API Error [{errcode}]: {errmsg}")


class TokenManager:
    """Access Token 管理器"""
    
    def __init__(self, appid: str, appsecret: str):
        self.appid = appid
        self.appsecret = appsecret
        self._access_token: Optional[str] = None
        self._expires_at: int = 0
    
    def get_token(self, force_refresh: bool = False) -> str:
        """
        获取 Access Token
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            Access Token 字符串
        """
        # 检查内存缓存
        if not force_refresh and self._access_token and time.time() < self._expires_at:
            return self._access_token
        
        # 检查文件缓存
        if not force_refresh:
            cached = config.get_cached_token()
            if cached and cached.get("appid") == self.appid:
                if time.time() < cached.get("expires_at", 0):
                    self._access_token = cached["access_token"]
                    self._expires_at = cached["expires_at"]
                    return self._access_token
        
        # 重新获取
        return self._fetch_token()
    
    def _fetch_token(self) -> str:
        """从微信服务器获取 Token"""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" in data:
                self._access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                self._expires_at = int(time.time()) + expires_in - 300  # 提前5分钟过期
                
                # 保存到缓存
                config.save_token(self._access_token, expires_in)
                
                return self._access_token
            else:
                errcode = data.get("errcode", -1)
                errmsg = data.get("errmsg", "Unknown error")
                raise WeChatAPIError(errcode, errmsg)
                
        except requests.RequestException as e:
            raise WeChatAPIError(-1, f"Network error: {str(e)}")
    
    def clear_cache(self):
        """清除 Token 缓存"""
        self._access_token = None
        self._expires_at = 0
        config.clear_token()


class WeChatAPI:
    """微信公众号 API 客户端"""
    
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    
    def __init__(self, appid: Optional[str] = None, appsecret: Optional[str] = None):
        self.appid = appid or config.get_appid()
        self.appsecret = appsecret or config.get_appsecret()
        
        if not self.appid or not self.appsecret:
            raise ValueError("AppID 和 AppSecret 不能为空，请通过环境变量或配置文件设置")
        
        self.token_manager = TokenManager(self.appid, self.appsecret)
    
    def _get_access_token(self) -> str:
        """获取 Access Token"""
        return self.token_manager.get_token()
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (get/post)
            endpoint: API 端点路径
            **kwargs: 请求参数
            
        Returns:
            API 响应数据
        """
        url = f"{self.API_BASE}{endpoint}"
        params = kwargs.pop("params", {})
        params["access_token"] = self._get_access_token()
        
        try:
            if method.lower() == "get":
                response = requests.get(url, params=params, **kwargs)
            else:
                response = requests.post(url, params=params, **kwargs)
            
            response.raise_for_status()
            data = response.json()
            
            # 检查微信 API 错误码
            errcode = data.get("errcode", 0)
            if errcode != 0:
                # Token 过期，尝试刷新后重试
                if errcode == 40001:
                    self.token_manager.clear_cache()
                    params["access_token"] = self._get_access_token()
                    if method.lower() == "get":
                        response = requests.get(url, params=params, **kwargs)
                    else:
                        response = requests.post(url, params=params, **kwargs)
                    data = response.json()
                    errcode = data.get("errcode", 0)
                
                if errcode != 0:
                    raise WeChatAPIError(errcode, data.get("errmsg", "Unknown error"))
            
            return data
            
        except requests.RequestException as e:
            raise WeChatAPIError(-1, f"Network error: {str(e)}")
    
    @retry_on_error(max_retries=3, backoff_factor=1.0)
    def upload_image(self, image_path: str) -> str:
        """
        上传图片到微信素材库
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片 URL
        """
        url = f"{self.API_BASE}/media/uploadimg"
        params = {"access_token": self._get_access_token()}
        
        with open(image_path, "rb") as f:
            files = {"media": f}
            response = requests.post(url, params=params, files=files)
        
        response.raise_for_status()
        data = response.json()
        
        if "url" in data:
            return data["url"]
        else:
            errcode = data.get("errcode", -1)
            errmsg = data.get("errmsg", "Upload failed")
            raise WeChatAPIError(errcode, errmsg)
    
    @retry_on_error(max_retries=3, backoff_factor=1.0)
    def add_draft(self, title: str, content: str, author: str = "", 
                  digest: str = "", content_source_url: str = "",
                  thumb_media_id: str = "", need_open_comment: int = 0,
                  only_fans_can_comment: int = 0) -> str:
        """
        新增草稿
        
        Args:
            title: 文章标题
            content: 文章内容（HTML 格式）
            author: 作者
            digest: 摘要
            content_source_url: 原文链接
            thumb_media_id: 封面图片素材 ID（不传或空字符串表示没有封面）
            need_open_comment: 是否开启评论（0/1）
            only_fans_can_comment: 是否仅粉丝可评论（0/1）
            
        Returns:
            草稿 media_id
        """
        endpoint = "/draft/add"
        
        # 构建文章数据，只包含非空字段
        article = {
            "title": title,
            "content": content,
        }
        
        # 可选字段，只有非空时才添加
        if author:
            article["author"] = author
        if digest:
            article["digest"] = digest
        if content_source_url:
            article["content_source_url"] = content_source_url
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id
        
        # 评论设置
        article["need_open_comment"] = need_open_comment
        article["only_fans_can_comment"] = only_fans_can_comment
        
        data = {"articles": [article]}
        
        # 调试输出
        import json
        print(f"[调试] 发送的数据: {json.dumps(data, ensure_ascii=False)[:500]}...")
        
        result = self._request("post", endpoint, json=data)
        return result.get("media_id")
    
    def update_draft(self, media_id: str, index: int, article: Dict) -> bool:
        """
        更新草稿
        
        Args:
            media_id: 草稿 media_id
            index: 要更新的文章索引（多图文）
            article: 文章内容字典
            
        Returns:
            是否成功
        """
        endpoint = "/draft/update"
        
        data = {
            "media_id": media_id,
            "index": index,
            "articles": article
        }
        
        result = self._request("post", endpoint, json=data)
        return result.get("errcode") == 0
    
    def get_draft(self, media_id: str) -> Dict:
        """
        获取草稿详情
        
        Args:
            media_id: 草稿 media_id
            
        Returns:
            草稿详情
        """
        endpoint = "/draft/get"
        params = {"media_id": media_id}
        
        return self._request("post", endpoint, params=params)
    
    def delete_draft(self, media_id: str) -> bool:
        """
        删除草稿
        
        Args:
            media_id: 草稿 media_id
            
        Returns:
            是否成功
        """
        endpoint = "/draft/delete"
        data = {"media_id": media_id}
        
        result = self._request("post", endpoint, json=data)
        return result.get("errcode") == 0
    
    def list_drafts(self, offset: int = 0, count: int = 20, 
                    no_content: int = 0) -> List[Dict]:
        """
        获取草稿列表
        
        Args:
            offset: 偏移量
            count: 返回数量（1-20）
            no_content: 是否不返回内容（1/0）
            
        Returns:
            草稿列表
        """
        endpoint = "/draft/batchget"
        data = {
            "offset": offset,
            "count": min(count, 20),
            "no_content": no_content
        }
        
        result = self._request("post", endpoint, json=data)
        return result.get("item", [])
    
    def get_draft_count(self) -> Dict:
        """
        获取草稿总数
        
        Returns:
            草稿数量信息
        """
        endpoint = "/draft/count"
        return self._request("get", endpoint)
