#!/usr/bin/env python3
"""
测试配置管理模块
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入要测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


class TestConfig:
    """测试 Config 类"""
    
    def setup_method(self):
        """每个测试方法运行前的准备"""
        # 创建一个临时配置目录
        self.test_config_dir = Path.home() / ".wechat-mp-publisher-test"
        self.test_config_dir.mkdir(exist_ok=True)
        
        # 创建 Config 实例
        self.config = Config()
        # 临时修改配置目录为测试目录
        self.config.config_dir = self.test_config_dir
        self.config.config_file = self.test_config_dir / "config.json"
        self.config.token_file = self.test_config_dir / "token.json"
    
    def teardown_method(self):
        """每个测试方法运行后的清理"""
        # 清理测试文件
        if self.test_config_dir.exists():
            import shutil
            shutil.rmtree(self.test_config_dir)
    
    def test_init_config(self):
        """测试配置初始化"""
        # 初始化配置
        config_file = self.config.init_config(
            appid="test_appid",
            appsecret="test_secret",
            author="测试作者"
        )
        
        # 验证配置文件是否创建
        assert self.config.config_file.exists()
        
        # 验证配置内容
        assert self.config.get_appid() == "test_appid"
        assert self.config.get_appsecret() == "test_secret"
        assert self.config.get("default.author") == "测试作者"
    
    def test_get_and_set(self):
        """测试获取和设置配置"""
        # 设置配置
        self.config.set("test.key", "test_value")
        
        # 获取配置
        value = self.config.get("test.key")
        assert value == "test_value"
    
    def test_get_default_value(self):
        """测试获取不存在的配置返回默认值"""
        # 获取不存在的配置
        value = self.config.get("nonexistent.key", "default")
        assert value == "default"
    
    def test_environment_variable_override(self):
        """测试环境变量覆盖配置文件"""
        # 先设置配置文件
        self.config.set("appid", "config_appid")
        
        # 设置环境变量
        os.environ["WECHAT_APPID"] = "env_appid"
        
        # 验证环境变量优先级更高
        assert self.config.get_appid() == "env_appid"
        
        # 清理环境变量
        del os.environ["WECHAT_APPID"]
    
    def test_token_cache(self):
        """测试 Token 缓存功能"""
        import time
        
        # 保存 Token
        self.config.save_token("test_token_123", 7200)
        
        # 验证 Token 文件存在
        assert self.config.token_file.exists()
        
        # 验证能读取到缓存的 Token
        cached = self.config.get_cached_token()
        assert cached is not None
        assert cached["access_token"] == "test_token_123"
        assert cached["expires_at"] > time.time()


# 如果这个文件直接运行，执行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
