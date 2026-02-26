#!/usr/bin/env python3
"""
主题管理模块
提供主题创建、编辑、预览、导入导出等功能
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from src.config import config


@dataclass
class ThemeConfig:
    """主题配置数据类"""
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    base_theme: str = "default"  # 继承自哪个基础主题
    
    # 颜色配置
    primary_color: str = "#07c160"  # 主色调（微信绿）
    text_color: str = "#333333"      # 正文颜色
    heading_color: str = "#000000"   # 标题颜色
    bg_color: str = "#ffffff"        # 背景颜色
    code_bg: str = "#f8f8f8"         # 代码背景
    quote_bg: str = "#f5f5f5"        # 引用背景
    link_color: str = "#07c160"      # 链接颜色
    
    # 字体配置
    font_family: str = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    font_size: str = "16px"
    line_height: str = "1.8"
    
    # 间距配置
    paragraph_spacing: str = "16px"
    heading_spacing: str = "24px"


class ThemeManager:
    """主题管理器"""
    
    # 内置主题列表
    BUILTIN_THEMES = ['default', 'tech', 'minimal', 'elegant']
    
    def __init__(self):
        self.custom_themes_dir = config.config_dir / "themes"
        self.custom_themes_dir.mkdir(parents=True, exist_ok=True)
    
    def list_themes(self) -> List[Dict]:
        """
        列出所有可用主题
        
        Returns:
            主题列表，每个主题包含名称、类型、描述等信息
        """
        themes = []
        
        # 内置主题
        for name in self.BUILTIN_THEMES:
            themes.append({
                'name': name,
                'type': 'builtin',
                'description': self._get_builtin_theme_desc(name),
                'path': str(Path(__file__).parent.parent / "themes" / f"{name}.css")
            })
        
        # 自定义主题
        if self.custom_themes_dir.exists():
            for css_file in self.custom_themes_dir.glob("*.css"):
                name = css_file.stem
                config_file = css_file.with_suffix('.json')
                
                theme_info = {
                    'name': name,
                    'type': 'custom',
                    'description': '用户自定义主题',
                    'path': str(css_file)
                }
                
                # 如果有配置文件，读取更多信息
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        theme_info['description'] = config_data.get('description', '用户自定义主题')
                        theme_info['author'] = config_data.get('author', '未知')
                        theme_info['version'] = config_data.get('version', '1.0.0')
                    except Exception:
                        pass
                
                themes.append(theme_info)
        
        return themes
    
    def _get_builtin_theme_desc(self, name: str) -> str:
        """获取内置主题描述"""
        descriptions = {
            'default': '默认主题，简洁大方，适合大多数文章',
            'tech': '技术主题，代码高亮优化，适合技术文章',
            'minimal': '极简主题，专注内容，无多余装饰',
            'elegant': '优雅主题，衬线字体，适合文学类文章'
        }
        return descriptions.get(name, '内置主题')
    
    def create_theme(self, name: str, config: ThemeConfig, save_dir: Optional[Path] = None) -> str:
        """
        创建新主题
        
        Args:
            name: 主题名称
            config: 主题配置
            save_dir: 指定保存目录（可选，默认使用用户配置目录）
            
        Returns:
            创建的主题文件路径
        """
        # 检查名称是否合法
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError("主题名称只能包含字母、数字、下划线和横线")
        
        if name in self.BUILTIN_THEMES:
            raise ValueError(f"'{name}' 是内置主题名称，请使用其他名称")
        
        # 确定保存目录
        if save_dir is None:
            theme_dir = self.custom_themes_dir
        else:
            theme_dir = Path(save_dir)
        
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        css_path = theme_dir / f"{name}.css"
        config_path = theme_dir / f"{name}.json"
        
        # 生成 CSS
        css_content = self._generate_css(config)
        
        # 保存 CSS 文件
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # 保存配置文件
        config_dict = asdict(config)
        config_dict['name'] = name
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        return str(css_path)
    
    def _generate_css(self, config: ThemeConfig) -> str:
        """
        根据配置生成 CSS
        
        Args:
            config: 主题配置
            
        Returns:
            CSS 内容
        """
        css = f"""/*
 * 主题: {config.name}
 * 描述: {config.description}
 * 作者: {config.author}
 * 版本: {config.version}
 */

.mp-article {{
    font-family: {config.font_family};
    font-size: {config.font_size};
    line-height: {config.line_height};
    color: {config.text_color};
    background-color: {config.bg_color};
    max-width: 100%;
    padding: 20px;
}}

/* 标题样式 */
.mp-article h1 {{
    font-size: 24px;
    font-weight: bold;
    color: {config.heading_color};
    margin: {config.heading_spacing} 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid {config.primary_color};
}}

.mp-article h2 {{
    font-size: 20px;
    font-weight: bold;
    color: {config.heading_color};
    margin: 20px 0 12px;
    padding-left: 12px;
    border-left: 4px solid {config.primary_color};
}}

.mp-article h3 {{
    font-size: 18px;
    font-weight: bold;
    color: {config.heading_color};
    margin: 16px 0 10px;
}}

/* 段落 */
.mp-article p {{
    margin: {config.paragraph_spacing} 0;
    text-align: justify;
    line-height: {config.line_height};
}}

/* 引用块 */
.mp-article blockquote {{
    margin: 16px 0;
    padding: 12px 16px;
    background: {config.quote_bg};
    border-left: 4px solid {config.primary_color};
    color: #666;
}}

/* 代码块 */
.mp-article pre {{
    background: {config.code_bg};
    padding: 16px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 14px;
    line-height: 1.5;
    margin: 16px 0;
}}

.mp-article code {{
    background: {config.code_bg};
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 14px;
}}

/* 链接 */
.mp-article a {{
    color: {config.link_color};
    text-decoration: none;
}}

.mp-article a:hover {{
    text-decoration: underline;
}}

/* 图片 */
.mp-article img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 16px auto;
}}

/* 表格 */
.mp-article table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 14px;
}}

.mp-article th,
.mp-article td {{
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}}

.mp-article th {{
    background: {config.quote_bg};
    font-weight: bold;
}}

/* 列表 */
.mp-article ul,
.mp-article ol {{
    margin: 16px 0;
    padding-left: 24px;
}}

.mp-article li {{
    margin: 8px 0;
    line-height: 1.6;
}}

/* 分隔线 */
.mp-article hr {{
    border: none;
    border-top: 1px solid #eee;
    margin: 24px 0;
}}
"""
        return css
    
    def get_theme_css(self, name: str) -> str:
        """
        获取主题 CSS 内容
        
        Args:
            name: 主题名称
            
        Returns:
            CSS 内容
        """
        # 如果 name 是文件路径，直接读取
        name_path = Path(name)
        if name_path.exists() and name_path.suffix == '.css':
            return name_path.read_text(encoding='utf-8')
        
        # 1. 查找当前目录的 .themes 文件夹
        local_theme_path = Path('.themes') / f"{name}.css"
        if local_theme_path.exists():
            return local_theme_path.read_text(encoding='utf-8')
        
        # 2. 查找用户配置目录的自定义主题
        custom_path = self.custom_themes_dir / f"{name}.css"
        if custom_path.exists():
            return custom_path.read_text(encoding='utf-8')
        
        # 3. 查找内置主题
        builtin_path = Path(__file__).parent.parent / "themes" / f"{name}.css"
        if builtin_path.exists():
            return builtin_path.read_text(encoding='utf-8')
        
        # 3. 返回默认主题
        default_path = Path(__file__).parent.parent / "themes" / "default.css"
        if default_path.exists():
            return default_path.read_text(encoding='utf-8')
        
        return ""
    
    def delete_theme(self, name: str) -> bool:
        """
        删除自定义主题
        
        Args:
            name: 主题名称
            
        Returns:
            是否成功删除
        """
        if name in self.BUILTIN_THEMES:
            raise ValueError(f"不能删除内置主题 '{name}'")
        
        css_path = self.custom_themes_dir / f"{name}.css"
        config_path = self.custom_themes_dir / f"{name}.json"
        
        deleted = False
        if css_path.exists():
            css_path.unlink()
            deleted = True
        if config_path.exists():
            config_path.unlink()
            deleted = True
        
        return deleted
    
    def export_theme(self, name: str, output_path: str) -> str:
        """
        导出主题为文件
        
        Args:
            name: 主题名称
            output_path: 输出路径
            
        Returns:
            导出的文件路径
        """
        css_content = self.get_theme_css(name)
        
        output = Path(output_path)
        output.write_text(css_content, encoding='utf-8')
        
        return str(output)
    
    def import_theme(self, css_path: str, name: Optional[str] = None) -> str:
        """
        导入外部主题文件
        
        Args:
            css_path: CSS 文件路径
            name: 主题名称（可选，默认使用文件名）
            
        Returns:
            导入后的主题路径
        """
        source = Path(css_path)
        if not source.exists():
            raise FileNotFoundError(f"文件不存在: {css_path}")
        
        theme_name = name or source.stem
        
        # 检查名称冲突
        if theme_name in self.BUILTIN_THEMES:
            theme_name = f"custom_{theme_name}"
        
        # 复制到自定义主题目录
        dest = self.custom_themes_dir / f"{theme_name}.css"
        dest.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
        
        # 创建基本配置
        config = ThemeConfig(
            name=theme_name,
            description=f"导入的主题: {source.name}",
            author="未知"
        )
        config_path = self.custom_themes_dir / f"{theme_name}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        
        return str(dest)


# 全局主题管理器实例
theme_manager = ThemeManager()
