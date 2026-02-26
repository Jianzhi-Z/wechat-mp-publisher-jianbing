#!/usr/bin/env python3
"""
GUI 预览窗口模块
提供可视化的文章预览和一键复制功能
"""

import webview
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup

from src.image_utils import convert_images_to_base64


class PreviewWindow:
    """预览窗口，支持一键复制"""
    
    def __init__(self, html_content: str, base_path: str = ".", title: str = "预览"):
        """
        初始化预览窗口
        
        Args:
            html_content: HTML 内容
            base_path: 基础路径（用于解析图片相对路径）
            title: 窗口标题
        """
        self.html = html_content
        self.base_path = base_path
        self.title = title
        self.window = None
    
    def show(self):
        """显示预览窗口"""
        # 注入复制按钮和脚本
        enhanced_html = self._inject_copy_script(self.html)
        
        # 创建窗口
        self.window = webview.create_window(
            title=self.title,
            html=enhanced_html,
            width=1000,
            height=800,
            resizable=True,
            min_size=(800, 600)
        )
        
        # 启动
        webview.start(debug=False)
    
    def _inject_copy_script(self, html: str) -> str:
        """
        注入复制按钮和脚本
        
        Args:
            html: 原始 HTML
            
        Returns:
            增强后的 HTML
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 添加浮动工具栏
        toolbar = soup.new_tag('div')
        toolbar['id'] = 'copy-toolbar'
        toolbar['style'] = '''
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #fff;
            border-bottom: 1px solid #e0e0e0;
            padding: 12px 20px;
            z-index: 9999;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        '''
        
        # 左侧标题
        title_span = soup.new_tag('span')
        title_span.string = '📝 文章预览'
        title_span['style'] = 'font-size: 16px; font-weight: bold; color: #333;'
        toolbar.append(title_span)
        
        # 右侧按钮组
        button_group = soup.new_tag('div')
        button_group['style'] = 'display: flex; gap: 10px;'
        
        # 复制按钮
        copy_btn = soup.new_tag('button')
        copy_btn.string = '📋 复制全部内容'
        copy_btn['onclick'] = 'copyContent()'
        copy_btn['style'] = '''
            background: #07c160;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        '''
        button_group.append(copy_btn)
        
        # 转换图片按钮（可选）
        convert_btn = soup.new_tag('button')
        convert_btn.string = '🖼️ 转换图片'
        convert_btn['onclick'] = 'convertImages()'
        convert_btn['style'] = '''
            background: #f5f5f5;
            color: #333;
            border: 1px solid #ddd;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        '''
        button_group.append(convert_btn)
        
        toolbar.append(button_group)
        
        # 添加提示信息区域
        msg_div = soup.new_tag('div')
        msg_div['id'] = 'message-area'
        msg_div['style'] = '''
            position: fixed;
            top: 60px;
            right: 20px;
            padding: 12px 20px;
            background: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 4px;
            display: none;
            z-index: 10000;
            font-size: 14px;
        '''
        
        # 添加样式
        style = soup.new_tag('style')
        style.string = '''
            body {
                margin: 0;
                padding-top: 60px !important;
            }
            .mp-article {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            #copy-toolbar button:hover {
                opacity: 0.9;
            }
            #copy-toolbar button:active {
                transform: scale(0.98);
            }
        '''
        
        # 添加脚本
        script = soup.new_tag('script')
        script.string = '''
            // 显示消息
            function showMessage(text, isError = false) {
                const msgArea = document.getElementById('message-area');
                msgArea.textContent = text;
                msgArea.style.background = isError ? '#ffebee' : '#e8f5e9';
                msgArea.style.borderColor = isError ? '#f44336' : '#4caf50';
                msgArea.style.display = 'block';
                setTimeout(() => {
                    msgArea.style.display = 'none';
                }, 3000);
            }
            
            // 复制内容
            function copyContent() {
                const content = document.querySelector('.mp-article');
                if (!content) {
                    showMessage('未找到文章内容', true);
                    return;
                }
                
                try {
                    // 使用 Clipboard API 复制富文本
                    const htmlContent = content.outerHTML;
                    const textContent = content.innerText;
                    
                    // 创建 Blob
                    const htmlBlob = new Blob([htmlContent], { type: 'text/html' });
                    const textBlob = new Blob([textContent], { type: 'text/plain' });
                    
                    // 创建 ClipboardItem
                    const item = new ClipboardItem({
                        'text/html': htmlBlob,
                        'text/plain': textBlob
                    });
                    
                    navigator.clipboard.write([item]).then(function() {
                        showMessage('✅ 已复制到剪贴板！请粘贴到公众号编辑器');
                    }, function(err) {
                        // 降级方案
                        fallbackCopy(content);
                    });
                } catch (err) {
                    fallbackCopy(content);
                }
            }
            
            // 降级复制方案
            function fallbackCopy(element) {
                const range = document.createRange();
                range.selectNode(element);
                
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                
                try {
                    document.execCommand('copy');
                    showMessage('✅ 已复制到剪贴板！请粘贴到公众号编辑器');
                } catch (err) {
                    showMessage('❌ 复制失败，请手动复制', true);
                }
                
                selection.removeAllRanges();
            }
            
            // 转换图片（预留接口，实际在 Python 中处理）
            function convertImages() {
                showMessage('🔄 图片转换功能需要重新打开预览窗口');
            }
        '''
        
        # 插入到文档中
        if soup.head:
            soup.head.append(style)
        else:
            # 如果没有 head，创建一个
            head = soup.new_tag('head')
            head.append(style)
            soup.html.insert(0, head)
        
        if soup.body:
            soup.body.insert_before(toolbar)
            soup.body.append(msg_div)
            soup.body.append(script)
        
        return str(soup)
    
    def _prepare_html_with_base64(self, html: str) -> str:
        """
        准备 HTML，将图片转换为 Base64
        
        Args:
            html: 原始 HTML
            
        Returns:
            处理后的 HTML
        """
        print("正在转换图片为 Base64，请稍候...")
        return convert_images_to_base64(html, self.base_path, compress=True)


def preview_with_copy(html_content: str, base_path: str = ".", title: str = "预览", convert_images: bool = True):
    """
    打开预览窗口，支持一键复制
    
    Args:
        html_content: HTML 内容
        base_path: 基础路径
        title: 窗口标题
        convert_images: 是否将图片转换为 Base64
    """
    if convert_images:
        html_content = convert_images_to_base64(html_content, base_path, compress=True)
    
    window = PreviewWindow(html_content, base_path, title)
    window.show()


if __name__ == '__main__':
    # 测试
    test_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            .mp-article { font-family: sans-serif; padding: 20px; }
            h1 { color: #07c160; }
        </style>
    </head>
    <body>
        <section class="mp-article">
            <h1>测试文章</h1>
            <p>这是一段测试内容。</p>
        </section>
    </body>
    </html>
    '''
    
    preview_with_copy(test_html, title="测试预览")
