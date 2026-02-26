#!/usr/bin/env python3
"""
Markdown 转换器模块
将 Markdown 转换为微信公众号兼容的 HTML
"""

import re
import markdown
from pathlib import Path
from typing import Optional, List
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class MarkdownConverter:
    """Markdown 到微信公众号 HTML 转换器"""
    
    def __init__(self, theme: str = "default"):
        """
        初始化转换器
        
        Args:
            theme: 主题名称
        """
        self.theme = theme
        self.theme_css = self._load_theme_css(theme)
        
        # 配置 Markdown 解析器
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists',  # 更好的列表处理
            ]
        )
    
    def _load_theme_css(self, theme: str) -> str:
        """
        加载主题 CSS
        
        Args:
            theme: 主题名称
            
        Returns:
            CSS 内容
        """
        from src.theme_manager import theme_manager
        return theme_manager.get_theme_css(theme)
    
    def _preprocess_markdown(self, markdown_text: str) -> str:
        """
        预处理 Markdown 文本
        - 处理删除线语法 ~~text~~
        
        Args:
            markdown_text: 原始 Markdown 文本
            
        Returns:
            预处理后的 Markdown 文本
        """
        # 处理删除线 ~~text~~ -> <del>text</del>
        # 使用正则表达式匹配，避免和代码块冲突
        lines = markdown_text.split('\n')
        result_lines = []
        in_code_block = False
        
        for line in lines:
            # 检测代码块边界
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            
            # 不在代码块内才处理删除线
            if not in_code_block:
                # 处理 ~~text~~ 为 <del>text</del>
                import re
                line = re.sub(r'~~(.*?)~~', r'<del>\1</del>', line)
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def convert(self, markdown_text: str, title: Optional[str] = None) -> str:
        """
        将 Markdown 文本转换为微信公众号 HTML
        
        Args:
            markdown_text: Markdown 文本
            title: 页面标题（用于浏览器标签页）
            
        Returns:
            微信公众号兼容的 HTML
        """
        # 0. 预处理 Markdown
        markdown_text = self._preprocess_markdown(markdown_text)
        
        # 1. 解析 Markdown 为 HTML
        html_content = self.md.convert(markdown_text)
        
        # 2. 处理代码高亮
        html_content = self._process_code_blocks(html_content)
        
        # 3. 处理图片标签
        html_content = self._process_images(html_content)
        
        # 4. 处理表格
        html_content = self._process_tables(html_content)
        
        # 5. 添加微信特定样式
        html_content = self._apply_wechat_styles(html_content)
        
        # 6. 清理不需要的属性
        html_content = self._clean_html(html_content)
        
        # 7. 包装为完整文章
        html_content = self._wrap_article(html_content, title=title)
        
        # 重置 Markdown 解析器状态
        self.md.reset()
        
        return html_content
    
    def convert_file(self, file_path: str, title: Optional[str] = None) -> str:
        """
        从文件读取并转换
        
        Args:
            file_path: Markdown 文件路径
            title: 页面标题（用于浏览器标签页）
            
        Returns:
            微信公众号兼容的 HTML
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return self.convert(content, title=title)
    
    def _process_code_blocks(self, html: str) -> str:
        """
        处理代码块，添加语法高亮
        
        Args:
            html: HTML 内容
            
        Returns:
            处理后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if not code:
                continue
            
            # 获取代码内容
            code_text = code.get_text()
            
            # 获取语言类名
            language = None
            if code.get('class'):
                for cls in code['class']:
                    if cls.startswith('language-'):
                        language = cls.replace('language-', '')
                        break
            
            # 语法高亮
            try:
                if language:
                    lexer = get_lexer_by_name(language)
                else:
                    lexer = guess_lexer(code_text)
                
                formatter = HtmlFormatter(
                    style='default',
                    noclasses=True,
                    prestyles='margin: 0; padding: 0; background: transparent;'
                )
                highlighted = highlight(code_text, lexer, formatter)
                
                # 替换 code 内容
                code.replace_with(BeautifulSoup(highlighted, 'html.parser').find('div') or 
                                  BeautifulSoup(highlighted, 'html.parser').find('pre'))
                
            except ClassNotFound:
                # 如果无法识别语言，保持原样
                pass
            
            # 设置 pre 标签样式
            pre['style'] = (
                'background: #f8f8f8;'
                'padding: 16px;'
                'border-radius: 4px;'
                'overflow-x: auto;'
                'font-family: Consolas, Monaco, monospace;'
                'font-size: 14px;'
                'line-height: 1.5;'
                'margin: 16px 0;'
            )
        
        # 处理行内代码
        for code in soup.find_all('code'):
            if not code.parent.name == 'pre':
                code['style'] = (
                    'background: #f0f0f0;'
                    'padding: 2px 6px;'
                    'border-radius: 3px;'
                    'font-family: Consolas, Monaco, monospace;'
                    'font-size: 14px;'
                    'color: #e83e8c;'
                )
        
        return str(soup)
    
    def _process_images(self, html: str) -> str:
        """
        处理图片标签，添加微信兼容样式
        
        Args:
            html: HTML 内容
            
        Returns:
            处理后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        for img in soup.find_all('img'):
            # 添加微信图片样式
            img['style'] = (
                'max-width: 100%;'
                'height: auto;'
                'display: block;'
                'margin: 16px auto;'
            )
            
            # 确保有 data-src（微信懒加载）
            if 'src' in img.attrs and 'data-src' not in img.attrs:
                img['data-src'] = img['src']
        
        return str(soup)
    
    def _process_tables(self, html: str) -> str:
        """
        处理表格，添加微信兼容样式
        
        Args:
            html: HTML 内容
            
        Returns:
            处理后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        for table in soup.find_all('table'):
            # 添加表格样式
            table['style'] = (
                'width: 100%;'
                'border-collapse: collapse;'
                'margin: 16px 0;'
                'font-size: 14px;'
            )
            
            # 处理表头
            for th in table.find_all('th'):
                th['style'] = (
                    'background: #f5f5f5;'
                    'border: 1px solid #ddd;'
                    'padding: 12px;'
                    'text-align: left;'
                    'font-weight: bold;'
                )
            
            # 处理单元格
            for td in table.find_all('td'):
                td['style'] = (
                    'border: 1px solid #ddd;'
                    'padding: 12px;'
                    'text-align: left;'
                )
        
        return str(soup)
    
    def _apply_wechat_styles(self, html: str) -> str:
        """
        应用微信特定样式
        
        Args:
            html: HTML 内容
            
        Returns:
            处理后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 处理标题
        for h1 in soup.find_all('h1'):
            h1['style'] = (
                'font-size: 24px;'
                'font-weight: bold;'
                'color: #000;'
                'margin: 24px 0 16px;'
                'padding-bottom: 8px;'
                'border-bottom: 2px solid #07c160;'
            )
        
        for h2 in soup.find_all('h2'):
            h2['style'] = (
                'font-size: 20px;'
                'font-weight: bold;'
                'color: #222;'
                'margin: 20px 0 12px;'
                'padding-left: 12px;'
                'border-left: 4px solid #07c160;'
            )
        
        for h3 in soup.find_all('h3'):
            h3['style'] = (
                'font-size: 18px;'
                'font-weight: bold;'
                'color: #333;'
                'margin: 16px 0 10px;'
            )
        
        # 处理段落
        for p in soup.find_all('p'):
            if 'style' not in p.attrs:
                p['style'] = (
                    'margin: 16px 0;'
                    'text-align: justify;'
                    'line-height: 1.8;'
                )
        
        # 处理引用块
        for blockquote in soup.find_all('blockquote'):
            blockquote['style'] = (
                'margin: 16px 0;'
                'padding: 12px 16px;'
                'background: #f5f5f5;'
                'border-left: 4px solid #07c160;'
                'color: #666;'
            )
        
        # 处理列表（保留嵌套结构）
        # 只处理顶级的 ul/ol，嵌套的保持原样
        for ul in soup.find_all('ul'):
            # 检查是否是嵌套列表（在 li 内部）
            if not ul.find_parent('li'):
                # 顶级列表
                ul['style'] = (
                    'margin: 16px 0;'
                    'padding-left: 24px;'
                )
            else:
                # 嵌套列表，添加缩进但减少外边距
                ul['style'] = (
                    'margin: 8px 0;'
                    'padding-left: 24px;'
                )
        
        for ol in soup.find_all('ol'):
            # 检查是否是嵌套列表
            if not ol.find_parent('li'):
                # 顶级列表
                ol['style'] = (
                    'margin: 16px 0;'
                    'padding-left: 24px;'
                )
            else:
                # 嵌套列表
                ol['style'] = (
                    'margin: 8px 0;'
                    'padding-left: 24px;'
                )
        
        for li in soup.find_all('li'):
            li['style'] = (
                'margin: 8px 0;'
                'line-height: 1.6;'
            )
        
        # 处理链接
        for a in soup.find_all('a'):
            a['style'] = (
                'color: #07c160;'
                'text-decoration: none;'
            )
        
        # 处理分隔线
        for hr in soup.find_all('hr'):
            hr['style'] = (
                'border: none;'
                'border-top: 1px solid #eee;'
                'margin: 24px 0;'
            )
        
        return str(soup)
    
    def _clean_html(self, html: str) -> str:
        """
        清理不需要的 HTML 属性
        
        Args:
            html: HTML 内容
            
        Returns:
            清理后的 HTML
        """
        # 移除 id 属性（微信不支持）
        soup = BeautifulSoup(html, 'html.parser')
        
        for tag in soup.find_all():
            if 'id' in tag.attrs:
                del tag['id']
            # 移除 class 属性（除了代码块的语言标记）
            if 'class' in tag.attrs:
                if tag.name != 'code':
                    del tag['class']
        
        return str(soup)
    
    def _wrap_article(self, html: str, title: Optional[str] = None) -> str:
        """
        包装为完整的微信文章 HTML
        
        Args:
            html: HTML 内容
            title: 页面标题（用于浏览器标签页）
            
        Returns:
            完整的 HTML
        """
        # 构建 title 标签
        title_tag = f"<title>{title}</title>" if title else ""
        
        # 构建完整 HTML
        full_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{title_tag}
<style>
{self.theme_css}
.mp-article {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    max-width: 100%;
    padding: 20px;
}}
</style>
</head>
<body>
<section class="mp-article">
{html}
</section>
</body>
</html>'''
        
        return full_html
    
    def extract_title(self, markdown_text: str) -> Optional[str]:
        """
        从 Markdown 文本中提取标题
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            标题或 None
        """
        # 匹配一级标题
        match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # 匹配二级标题
        match = re.search(r'^##\s+(.+)$', markdown_text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def extract_images(self, markdown_text: str) -> List[str]:
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
