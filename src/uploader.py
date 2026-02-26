#!/usr/bin/env python3
"""
图片上传处理器模块
处理 HTML 中的图片，上传到微信素材库并替换 URL
"""

import re
import requests
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

from src.wechat_api import WeChatAPI
from src.config import config
from src.image_utils import compress_image


class ImageProcessor:
    """图片处理器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    # 自动压缩阈值（字节）
    COMPRESS_THRESHOLD = 500 * 1024  # 500KB
    MAX_WIDTH = 1080  # 最大宽度
    JPEG_QUALITY = 85  # JPEG 质量
    
    def __init__(self, wechat_api: Optional[WeChatAPI] = None, 
                 auto_compress: bool = True,
                 max_width: int = None,
                 quality: int = None):
        """
        初始化图片处理器
        
        Args:
            wechat_api: 微信 API 实例，如果为 None 则自动创建
            auto_compress: 是否自动压缩过大的图片
            max_width: 压缩后的最大宽度（默认 1080）
            quality: JPEG 压缩质量（默认 85）
        """
        self.api = wechat_api or WeChatAPI()
        self._url_cache: Dict[str, str] = {}  # 本地路径 -> 微信 URL 缓存
        self.auto_compress = auto_compress
        self.max_width = max_width or self.MAX_WIDTH
        self.quality = quality or self.JPEG_QUALITY
    
    def process_html(self, html: str, base_path: Optional[str] = None, 
                     remove_failed: bool = True) -> Tuple[str, List[str], List[str]]:
        """
        处理 HTML 中的图片
        
        Args:
            html: HTML 内容
            base_path: 基础路径（用于解析相对路径）
            remove_failed: 是否移除上传失败的图片（默认True，微信草稿需要）
            
        Returns:
            (处理后的 HTML, 成功上传的图片列表, 失败的图片列表)
        """
        soup = BeautifulSoup(html, 'html.parser')
        success_list = []
        fail_list = []
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not src:
                continue
            
            # 跳过已经是微信域名的图片
            if 'mmbiz.qpic.cn' in src or 'mmbizurl.cn' in src:
                continue
            
            try:
                # 获取图片的绝对路径
                image_path = self._resolve_image_path(src, base_path)
                if not image_path:
                    fail_list.append(src)
                    if remove_failed:
                        img.decompose()  # 从 HTML 中移除失败的图片
                    continue
                
                # 检查缓存
                if image_path in self._url_cache:
                    wechat_url = self._url_cache[image_path]
                else:
                    # 自动压缩图片（如果启用且图片过大）
                    upload_path = image_path
                    if self.auto_compress:
                        from pathlib import Path as P
                        file_size = P(image_path).stat().st_size
                        if file_size > self.COMPRESS_THRESHOLD:
                            print(f"   [COMPRESS] 图片 {P(image_path).name} ({file_size/1024:.1f}KB) 超过阈值，正在压缩...")
                            compressed = compress_image(
                                image_path, 
                                max_width=self.max_width,
                                quality=self.quality
                            )
                            if compressed and compressed != image_path:
                                new_size = P(compressed).stat().st_size
                                print(f"   [COMPRESS] 压缩完成: {file_size/1024:.1f}KB -> {new_size/1024:.1f}KB")
                                upload_path = compressed
                    
                    # 上传到微信
                    wechat_url = self.api.upload_image(upload_path)
                    self._url_cache[image_path] = wechat_url
                
                # 替换 URL
                img['src'] = wechat_url
                img['data-src'] = wechat_url
                
                success_list.append(src)
                
            except Exception as e:
                print(f"警告: 上传图片失败 {src}: {e}")
                fail_list.append(src)
                if remove_failed:
                    img.decompose()  # 从 HTML 中移除失败的图片
        
        return str(soup), success_list, fail_list
    
    def _resolve_image_path(self, src: str, base_path: Optional[str] = None) -> Optional[str]:
        """
        解析图片路径
        
        Args:
            src: 图片路径（相对、绝对或 URL）
            base_path: 基础路径
            
        Returns:
            本地图片的绝对路径，如果是远程图片则下载后返回临时路径
        """
        # 如果是 URL，下载到临时目录
        if src.startswith(('http://', 'https://')):
            return self._download_image(src)
        
        # 如果是绝对路径
        path = Path(src)
        if path.is_absolute():
            if path.exists():
                return str(path)
            return None
        
        # 如果是相对路径，相对于 base_path 或当前目录
        if base_path:
            base = Path(base_path)
            if base.is_file():
                base = base.parent
            full_path = base / src
        else:
            full_path = Path.cwd() / src
        
        if full_path.exists():
            return str(full_path.resolve())
        
        return None
    
    def _download_image(self, url: str) -> Optional[str]:
        """
        下载远程图片到临时目录
        
        Args:
            url: 图片 URL
            
        Returns:
            本地临时文件路径
        """
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 从 URL 获取文件名
            parsed = urlparse(url)
            filename = Path(parsed.path).name
            if not filename:
                filename = 'downloaded_image.jpg'
            
            # 确保扩展名正确
            suffix = Path(filename).suffix.lower()
            if suffix not in self.SUPPORTED_FORMATS:
                # 从 Content-Type 推断
                content_type = response.headers.get('Content-Type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    suffix = '.jpg'
                elif 'png' in content_type:
                    suffix = '.png'
                elif 'gif' in content_type:
                    suffix = '.gif'
                else:
                    suffix = '.jpg'
                filename = f"image{suffix}"
            
            # 保存到临时目录
            temp_dir = Path.home() / ".wechat-mp-publisher" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_path = temp_dir / filename
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(temp_path)
            
        except Exception as e:
            print(f"警告: 下载图片失败 {url}: {e}")
            return None
    
    def validate_image(self, image_path: str) -> Tuple[bool, str]:
        """
        验证图片是否符合微信要求
        
        Args:
            image_path: 图片路径
            
        Returns:
            (是否有效, 错误信息)
        """
        path = Path(image_path)
        
        # 检查文件是否存在
        if not path.exists():
            return False, f"文件不存在: {image_path}"
        
        # 检查格式
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            return False, f"不支持的图片格式: {suffix}"
        
        # 检查大小（2MB 限制）
        size = path.stat().st_size
        if size > 2 * 1024 * 1024:
            return False, f"图片大小超过 2MB: {size / 1024 / 1024:.2f}MB"
        
        return True, ""
    
    def compress_image(self, image_path: str, max_size: int = 2 * 1024 * 1024, 
                       quality: int = 85) -> str:
        """
        压缩图片到指定大小以下
        
        Args:
            image_path: 原图片路径
            max_size: 最大大小（字节）
            quality: JPEG 质量
            
        Returns:
            压缩后的图片路径（如果不需要压缩则返回原路径）
        """
        from PIL import Image
        
        path = Path(image_path)
        size = path.stat().st_size
        
        # 如果已经小于限制，直接返回
        if size <= max_size:
            return image_path
        
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为 RGB（如果是 RGBA 或 P 模式）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 临时目录
                temp_dir = Path.home() / ".wechat-mp-publisher" / "temp"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # 压缩后的路径
                compressed_path = temp_dir / f"compressed_{path.name}"
                
                # 尝试不同质量级别
                for q in range(quality, 20, -10):
                    img.save(compressed_path, 'JPEG', quality=q, optimize=True)
                    
                    if compressed_path.stat().st_size <= max_size:
                        return str(compressed_path)
                
                # 如果还是太大，缩小尺寸
                ratio = 0.9
                while compressed_path.stat().st_size > max_size and ratio > 0.3:
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    resized = img.resize(new_size, Image.Resampling.LANCZOS)
                    resized.save(compressed_path, 'JPEG', quality=70, optimize=True)
                    ratio -= 0.1
                
                return str(compressed_path)
                
        except Exception as e:
            print(f"警告: 压缩图片失败 {image_path}: {e}")
            return image_path
    
    def extract_images_from_markdown(self, markdown_text: str) -> List[str]:
        """
        从 Markdown 文本中提取图片路径
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            图片路径列表
        """
        # 匹配 Markdown 图片语法 ![alt](url)
        pattern = r'!\[.*?\]\((.+?)\)'
        matches = re.findall(pattern, markdown_text)
        return matches
    
    def extract_images_from_html(self, html: str) -> List[str]:
        """
        从 HTML 中提取图片 URL
        
        Args:
            html: HTML 内容
            
        Returns:
            图片 URL 列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and src not in images:
                images.append(src)
        
        return images
