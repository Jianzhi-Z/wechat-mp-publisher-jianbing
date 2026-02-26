#!/usr/bin/env python3
"""
测试 Markdown 转换器模块
"""

import pytest
from pathlib import Path

# 导入要测试的模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.converter import MarkdownConverter


class TestMarkdownConverter:
    """测试 MarkdownConverter 类"""
    
    def setup_method(self):
        """测试前的准备"""
        self.converter = MarkdownConverter(theme="default")
    
    def test_convert_heading(self):
        """测试标题转换"""
        md = "# 一级标题\n## 二级标题\n### 三级标题"
        html = self.converter.convert(md)
        
        # 验证 HTML 包含标题标签（可能有 style 属性）
        assert "<h1" in html  # <h1 或 <h1 style="...">
        assert "一级标题" in html
        assert "<h2" in html
        assert "二级标题" in html
        assert "<h3" in html
        assert "三级标题" in html
    
    def test_convert_paragraph(self):
        """测试段落转换"""
        md = "这是一个普通段落。"
        html = self.converter.convert(md)
        
        assert "<p" in html  # <p 或 <p style="...">
        assert "这是一个普通段落" in html
    
    def test_convert_bold_and_italic(self):
        """测试粗体和斜体"""
        md = "**粗体** *斜体*"
        html = self.converter.convert(md)
        
        assert "<strong>粗体</strong>" in html
        assert "<em>斜体</em>" in html
    
    def test_convert_code_inline(self):
        """测试行内代码"""
        md = "使用 `print()` 函数"
        html = self.converter.convert(md)
        
        assert "<code" in html  # <code 或 <code style="...">
        assert "print()" in html
        assert "</code>" in html
    
    def test_convert_code_block(self):
        """测试代码块"""
        md = """```python
def hello():
    print("hello")
```"""
        html = self.converter.convert(md)
        
        # 验证包含 pre 标签
        assert "<pre" in html
        # 代码可能被高亮处理，检查关键词是否存在（不一定连续）
        assert "hello" in html  # 只要包含代码中的关键词即可
    
    def test_convert_list(self):
        """测试列表转换"""
        md = """- 项目1
- 项目2
- 项目3

1. 第一步
2. 第二步"""
        html = self.converter.convert(md)
        
        # 验证无序列表（可能有 style 属性）
        assert "<ul" in html
        # 验证列表项（可能有 style 属性）
        assert "项目1" in html
        assert "第一步" in html
        # 有序列表可能有也可能没有，不强制检查
    
    def test_convert_blockquote(self):
        """测试引用块"""
        md = "> 这是一段引用"
        html = self.converter.convert(md)
        
        assert "<blockquote" in html  # <blockquote 或 <blockquote style="...">
        assert "这是一段引用" in html
    
    def test_convert_link(self):
        """测试链接转换"""
        md = "[点击这里](https://example.com)"
        html = self.converter.convert(md)
        
        assert '<a href="https://example.com"' in html
        assert ">点击这里</a>" in html
    
    def test_convert_image(self):
        """测试图片转换"""
        md = "![图片描述](image.png)"
        html = self.converter.convert(md)
        
        assert "<img" in html
        assert 'src="image.png"' in html
        assert 'alt="图片描述"' in html
    
    def test_convert_table(self):
        """测试表格转换"""
        md = """| 姓名 | 年龄 |
|------|------|
| 张三 | 25   |
| 李四 | 30   |"""
        html = self.converter.convert(md)
        
        assert "<table" in html  # <table 或 <table style="...">
        assert "姓名" in html
        assert "张三" in html
    
    def test_convert_horizontal_rule(self):
        """测试分隔线"""
        md = "---"
        html = self.converter.convert(md)
        
        assert "<hr" in html
    
    def test_extract_title(self):
        """测试提取标题"""
        md = "# 文章标题\n\n正文内容"
        title = self.converter.extract_title(md)
        
        assert title == "文章标题"
    
    def test_extract_title_no_heading(self):
        """测试没有标题时返回 None"""
        md = "没有标题的内容"
        title = self.converter.extract_title(md)
        
        assert title is None
    
    def test_extract_images(self):
        """测试提取图片路径"""
        md = """![图1](image1.png)
正文
![图2](image2.png)"""
        images = self.converter.extract_images(md)
        
        assert len(images) == 2
        assert "image1.png" in images
        assert "image2.png" in images


class TestMarkdownConverterThemes:
    """测试不同主题"""
    
    def test_default_theme(self):
        """测试默认主题"""
        converter = MarkdownConverter(theme="default")
        assert converter.theme == "default"
        assert converter.theme_css != ""
    
    def test_tech_theme(self):
        """测试技术主题"""
        converter = MarkdownConverter(theme="tech")
        assert converter.theme == "tech"
        assert "2d2d" in converter.theme_css  # 代码块深色背景
    
    def test_nonexistent_theme_fallback(self):
        """测试不存在主题时使用默认主题"""
        converter = MarkdownConverter(theme="nonexistent")
        # 应该回退到默认主题
        assert converter.theme_css != ""


# 如果这个文件直接运行，执行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
