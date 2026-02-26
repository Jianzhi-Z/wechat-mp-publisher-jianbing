#!/usr/bin/env python3
"""
日志管理模块
提供统一的日志配置和管理
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.config import config


class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if LoggerManager._initialized:
            return
        
        self.logger = logging.getLogger("wechat_mp_publisher")
        self.logger.setLevel(logging.DEBUG)
        self._handlers = {}
        
        # 默认配置
        self.log_dir = config.config_dir / "logs"
        self.log_level = logging.INFO
        self.max_bytes = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        
        LoggerManager._initialized = True
    
    def setup(self, level: Optional[str] = None, 
              log_file: bool = True,
              console: bool = True):
        """
        配置日志
        
        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
            log_file: 是否写入文件
            console: 是否输出到控制台
        """
        # 清除现有处理器
        self.logger.handlers = []
        
        # 设置日志级别
        if level:
            self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        
        # 格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self._handlers['console'] = console_handler
        
        # 文件处理器
        if log_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # 主日志文件（轮转）
            main_log = self.log_dir / "app.log"
            file_handler = logging.handlers.RotatingFileHandler(
                main_log,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self._handlers['file'] = file_handler
            
            # 错误日志文件（单独记录错误）
            error_log = self.log_dir / "error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
            self._handlers['error'] = error_handler
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """获取日志记录器"""
        if name:
            return self.logger.getChild(name)
        return self.logger
    
    def set_level(self, level: str):
        """设置日志级别"""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        for handler in self._handlers.values():
            handler.setLevel(self.log_level)


# 全局日志管理器实例
logger_manager = LoggerManager()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return logger_manager.get_logger(name)


def init_logger(level: str = "INFO", log_file: bool = True, console: bool = True):
    """初始化日志系统"""
    logger_manager.setup(level=level, log_file=log_file, console=console)
    logger = get_logger()
    logger.info(f"日志系统初始化完成，级别: {level}")
    return logger
