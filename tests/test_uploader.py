#!/usr/bin/env python3
"""
测试图片上传处理器模块
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 导入要测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.uploader import ImageProcessor


class TestImageProcessor:
    """测试 ImageProcessor 类"""
    
    def setup_method(self):
        """测试前的准备"""
        # 创建一个模拟的 WeChatAPI
        self.mock_api = Mock()
        self.processor = ImageProcessor(wechat_api=self.mock_api)
    
    def test_validate_image_supported_format(self):
        """测试支持的图片格式验证"""
        # 创建一个临时图片文件
        test_image = Path(__file__).parent / "fixtures" / "test.jpg"
        test_image.parent.mkdir(exist_ok=True)
        
        # 创建一个空的 jpg 文件
        test_image.write_bytes(b"fake image data")
        
        try:
            is_valid, error = self.processor.validate_image(str(test_image))
            # 格式是支持的，但文件大小可能不符合要求
            assert is_valid  # 空文件也会通过验证
        finally:
            # 清理
            if test_image.exists():
                test_image.unlink()
    
    def test_validate_image_unsupported_format(self):
        """测试不支持的图片格式"""
        # 创建一个临时 txt 文件
        test_file = Path(__file__).parent / "fixtures" / "test.txt"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("not an image")
        
        try:
            is_valid, error = self.processor.validate_image(str(test_file))
            assert not is_valid
            assert "不支持的图片格式" in error
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_validate_image_not_exist(self):
        """测试不存在的文件"""
        is_valid, error = self.processor.validate_image("/path/not/exist.jpg")
        assert not is_valid
        assert "文件不存在" in error
    
    def test_extract_images_from_markdown(self):
        """测试从 Markdown 提取图片"""
        md = """![图1](image1.png)
正文内容
![图2](path/to/image2.jpg)"""
        
        images = self.processor.extract_images_from_markdown(md)
        
        assert len(images) == 2
        assert "image1.png" in images
        assert "path/to/image2.jpg" in images
    
    def test_extract_images_from_html(self):
        """测试从 HTML 提取图片"""
        html = '''<p>正文</p>
<img src="image1.png" alt="图1">
<img src="image2.jpg">
<p>结尾</p>'''
        
        images = self.processor.extract_images_from_html(html)
        
        assert len(images) == 2
        assert "image1.png" in images
        assert "image2.jpg" in images
    
    def test_process_html_skip_wechat_images(self):
        """测试跳过已经是微信域名的图片"""
        html = '<img src="https://mmbiz.qpic.cn/some/image.jpg">'
        
        result, success, fail = self.processor.process_html(html)
        
        # 不应该调用上传 API
        self.mock_api.upload_image.assert_not_called()
        assert len(success) == 0
        assert len(fail) == 0
    
    def test_process_html_upload_local_image(self):
        """测试上传本地图片"""
        # 创建临时图片文件
        test_image = Path(__file__).parent / "fixtures" / "local.png"
        test_image.parent.mkdir(exist_ok=True)
        test_image.write_bytes(b"fake image data")
        
        try:
            # 设置模拟返回值
            self.mock_api.upload_image.return_value = "https://mmbiz.qpic.cn/new/image.jpg"
            
            html = f'<img src="{test_image}">'
            result, success, fail = self.processor.process_html(html, base_path=str(test_image.parent))
            
            # 验证 API 被调用
            self.mock_api.upload_image.assert_called_once()
            # 验证 URL 被替换
            assert "mmbiz.qpic.cn/new/image.jpg" in result
            assert len(success) == 1
            
        finally:
            if test_image.exists():
                test_image.unlink()
    
    @patch('src.uploader.requests.get')
    def test_download_image(self, mock_get):
        """测试下载远程图片"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b"fake", b" image", b" data"])
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试下载
        local_path = self.processor._download_image("https://example.com/image.jpg")
        
        # 验证下载成功
        assert local_path is not None
        assert Path(local_path).exists()
        
        # 清理
        if local_path and Path(local_path).exists():
            Path(local_path).unlink()


# 如果这个文件直接运行，执行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
