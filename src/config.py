#!/usr/bin/env python3
"""
配置管理模块
处理配置文件读写、环境变量、Token 缓存等
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class Config:
    """配置管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "version": "0.1.0",
        "default": {
            "theme": "default",
            "author": "",
            "comment_enabled": False,
            "fans_only_comment": False
        },
        "image": {
            "max_width": 1080,
            "quality": 85,
            "format": "jpeg",
            "auto_compress": True
        },
        "upload": {
            "retry_times": 3,
            "retry_delay": 2
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".wechat-mp-publisher"
        self.config_file = self.config_dir / "config.json"
        self.token_file = self.config_dir / "token.json"
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"警告: 加载配置文件失败，使用默认配置: {e}")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置到文件"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项，优先级：环境变量 > 配置文件 > 默认值
        
        Args:
            key: 配置键，支持点号分隔，如 "default.theme"
            default: 默认值
        """
        # 首先检查环境变量（转换为大写，点号转下划线）
        env_key = key.replace(".", "_").upper()
        env_value = os.getenv(f"WECHAT_{env_key}") or os.getenv(env_key)
        if env_value:
            return env_value
        
        # 从配置文件获取
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置项
        
        Args:
            key: 配置键，支持点号分隔
            value: 配置值
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
    
    def get_appid(self) -> Optional[str]:
        """获取 AppID"""
        return os.getenv("WECHAT_APPID") or self._config.get("appid")
    
    def get_appsecret(self) -> Optional[str]:
        """获取 AppSecret"""
        return os.getenv("WECHAT_APPSECRET") or self._config.get("appsecret")
    
    # Token 缓存相关
    def get_cached_token(self) -> Optional[Dict]:
        """获取缓存的 Token"""
        if not self.token_file.exists():
            return None
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_token(self, access_token: str, expires_in: int):
        """
        保存 Token 到缓存
        
        Args:
            access_token: 访问令牌
            expires_in: 过期时间（秒）
        """
        import time
        token_data = {
            "access_token": access_token,
            "expires_at": int(time.time()) + expires_in - 300,  # 提前5分钟过期
            "appid": self.get_appid()
        }
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        # 设置文件权限（仅当前用户可读写）
        os.chmod(self.token_file, 0o600)
    
    def clear_token(self):
        """清除缓存的 Token"""
        if self.token_file.exists():
            self.token_file.unlink()
    
    def init_config(self, appid: str = "", appsecret: str = "", author: str = ""):
        """
        初始化配置文件
        
        Args:
            appid: 微信公众号 AppID
            appsecret: 微信公众号 AppSecret
            author: 默认作者名称
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = self.DEFAULT_CONFIG.copy()
        if appid:
            config["appid"] = appid
        if appsecret:
            config["appsecret"] = appsecret
        if author:
            config["default"]["author"] = author
        
        self._config = config
        self.save_config()
        
        # 创建自定义主题目录
        custom_themes_dir = self.config_dir / "themes"
        custom_themes_dir.mkdir(exist_ok=True)
        
        return self.config_file


# 全局配置实例
config = Config()
