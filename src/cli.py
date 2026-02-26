#!/usr/bin/env python3
"""
CLI 入口模块
提供命令行交互界面
"""

import os
import re
import sys
import json
import click
from pathlib import Path
from typing import Optional

from src.config import config
from src.converter import MarkdownConverter
from src.uploader import ImageProcessor
from src.wechat_api import WeChatAPI, WeChatAPIError
from src.logger import init_logger, get_logger


@click.group()
@click.version_option(version="1.1.0", prog_name="wechat-publisher")
@click.option('--verbose', '-v', is_flag=True, help='显示详细日志')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.pass_context
def cli(ctx, verbose, debug):
    """微信公众号文章发布工具 - 将 Markdown 转换为微信草稿"""
    # 初始化日志系统
    log_level = "DEBUG" if debug else ("INFO" if verbose else "WARNING")
    init_logger(level=log_level, log_file=True, console=True)


def _get_markdown_files(paths: list) -> list:
    """从路径列表中获取所有 Markdown 文件"""
    files = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix.lower() in ['.md', '.markdown']:
            files.append(path)
        elif path.is_dir():
            # 递归查找目录下的所有 .md 文件
            files.extend(path.rglob("*.md"))
            files.extend(path.rglob("*.markdown"))
    return sorted(set(files))


@cli.command()
@click.argument('paths', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('-t', '--title', help='文章标题（默认从 Markdown 提取，批量转换时自动生成）')
@click.option('-a', '--author', help='作者名称')
@click.option('-c', '--cover', type=click.Path(exists=True), help='封面图片路径')
@click.option('-d', '--draft', is_flag=True, help='保存到微信草稿箱')
@click.option('-p', '--preview', is_flag=True, help='生成本地预览文件')
@click.option('-o', '--output', type=click.Path(), help='输出 HTML 文件路径（批量转换时使用 --output-dir）')
@click.option('--output-dir', type=click.Path(), help='批量转换时的输出目录')
@click.option('--theme', default='default', help='使用主题（default/tech/minimal）')
@click.option('--digest', help='文章摘要')
@click.option('--source-url', help='原文链接')
@click.option('--comment/--no-comment', default=False, help='是否开启评论')
@click.option('--fans-comment', is_flag=True, help='仅粉丝可评论')
@click.option('--upload-images/--no-upload-images', default=True, help='是否上传图片')
@click.option('--compress/--no-compress', default=True, help='是否自动压缩过大的图片（默认开启）')
@click.option('--base64', 'use_base64', is_flag=True, help='将图片转为 Base64 嵌入 HTML（生成独立 HTML 文件）')
@click.option('--batch', is_flag=True, help='强制批量模式（即使只有一个文件）')
def convert(paths, title, author, cover, draft, preview, output, output_dir, theme, 
            digest, source_url, comment, fans_comment, upload_images, compress, use_base64, batch):
    """
    转换 Markdown 文件为微信公众号格式
    
    支持单个文件、多个文件或目录批量转换
    
    PATHS: Markdown 文件路径或目录（支持多个）
    
    示例:
        # 转换单个文件
        wechat-publisher convert article.md --preview
        
        # 转换多个文件
        wechat-publisher convert article1.md article2.md --preview
        
        # 转换整个目录
        wechat-publisher convert articles/ --preview --output-dir output/
        
        # 发布到草稿箱
        wechat-publisher convert article.md --draft --cover cover.jpg
    """
    # 获取所有要处理的 Markdown 文件
    files = _get_markdown_files(paths)
    
    if not files:
        click.echo("[ERROR] 未找到 Markdown 文件", err=True)
        sys.exit(1)
    
    # 判断是否为批量模式
    is_batch = batch or len(files) > 1
    
    if is_batch and output:
        click.echo("[ERROR] 批量转换时请使用 --output-dir 指定输出目录，而非 -o", err=True)
        sys.exit(1)
    
    click.echo(f"\n[INFO] 找到 {len(files)} 个 Markdown 文件")
    
    # 批量转换统计
    success_count = 0
    fail_count = 0
    results = []
    
    for idx, md_path in enumerate(files, 1):
        if is_batch:
            click.echo(f"\n{'='*60}")
            click.echo(f"[ {idx}/{len(files)} ] 正在处理: {md_path}")
            click.echo('='*60)
        
        try:
            # 1. 读取 Markdown 文件
            click.echo(f"📖 正在读取文件: {md_path}")
            markdown_content = md_path.read_text(encoding='utf-8')
            
            # 2. 提取标题（如果未指定）
            file_title = title
            if not file_title:
                converter_temp = MarkdownConverter()
                file_title = converter_temp.extract_title(markdown_content)
                if not file_title:
                    file_title = md_path.stem
                click.echo(f"[DRAFT] 使用标题: {file_title}")
            
            # 3. 转换 Markdown 为 HTML
            click.echo(f"THEME: 正在转换（主题: {theme}）...")
            converter = MarkdownConverter(theme=theme)
            html_content = converter.convert_file(str(md_path), title=file_title)
            
            # 4. 处理图片上传
            if draft and upload_images:
                click.echo("[IMAGE]  正在处理图片...")
                try:
                    api = WeChatAPI()
                    processor = ImageProcessor(api, auto_compress=compress)
                    # 微信草稿要求所有图片必须上传到微信，失败的要移除
                    html_content, success_list, fail_list = processor.process_html(
                        html_content, 
                        base_path=str(md_path.parent),
                        remove_failed=True  # 失败的图片会从 HTML 中移除
                    )
                    click.echo(f"   ✓ 成功上传 {len(success_list)} 张图片")
                    if fail_list:
                        click.echo(f"   [WARN]  移除 {len(fail_list)} 张无法上传的图片（微信草稿要求）")
                        for fail in fail_list:
                            click.echo(f"     - {fail}")
                except Exception as e:
                    click.echo(f"   [WARN]  图片处理失败: {e}", err=True)
            
            # 5. 处理 Base64 图片转换（生成独立 HTML）
            if use_base64:
                from src.image_utils import convert_images_to_base64
                click.echo("[BASE64] 正在将图片转换为 Base64...")
                html_content = convert_images_to_base64(html_content, str(md_path.parent))
                click.echo("   ✓ 图片已嵌入 HTML")
            
            # 6. 保存预览文件
            if preview or (is_batch and output_dir) or use_base64:
                if is_batch and output_dir:
                    # 批量模式：使用输出目录
                    out_dir = Path(output_dir)
                    out_dir.mkdir(parents=True, exist_ok=True)
                    output_path = out_dir / f"{md_path.stem}.html"
                else:
                    # 单文件模式
                    output_path = Path(output) if output else Path(f"{md_path.stem}.html")
                
                output_path.write_text(html_content, encoding='utf-8')
                click.echo(f"[OK] HTML 文件已保存: {output_path}")
                
                # 如果是 Base64 模式，显示文件大小
                if use_base64:
                    file_size = output_path.stat().st_size
                    click.echo(f"   文件大小: {file_size / 1024:.1f} KB")
            
            # 6. 发布到微信草稿箱
            if draft:
                click.echo("🚀 正在发布到微信草稿箱...")
                
                try:
                    api = WeChatAPI()
                    
                    # 处理封面图片
                    thumb_media_id = ""
                    if cover:
                        click.echo(f"📷 正在上传封面图片...")
                        click.echo("   [WARN] 封面图片上传暂未实现，请手动设置")
                    
                    # 发布草稿
                    media_id = api.add_draft(
                        title=file_title,
                        content=html_content,
                        author=author or config.get("default.author", ""),
                        digest=digest or "",
                        content_source_url=source_url or "",
                        thumb_media_id=thumb_media_id,
                        need_open_comment=1 if comment else 0,
                        only_fans_can_comment=1 if fans_comment else 0
                    )
                    
                    click.echo(f"[OK] 草稿发布成功！Media ID: {media_id}")
                    results.append({'file': str(md_path), 'status': 'success', 'media_id': media_id})
                    
                except WeChatAPIError as e:
                    click.echo(f"[ERROR] 微信 API 错误: {e}", err=True)
                    fail_count += 1
                    results.append({'file': str(md_path), 'status': 'failed', 'error': str(e)})
                    continue
                except Exception as e:
                    click.echo(f"[ERROR] 发布失败: {e}", err=True)
                    fail_count += 1
                    results.append({'file': str(md_path), 'status': 'failed', 'error': str(e)})
                    continue
            
            success_count += 1
            
        except Exception as e:
            click.echo(f"[ERROR] 处理文件失败: {e}", err=True)
            fail_count += 1
            results.append({'file': str(md_path), 'status': 'failed', 'error': str(e)})
    
    # 批量模式输出汇总
    if is_batch:
        click.echo(f"\n{'='*60}")
        click.echo("[SUMMARY] 批量转换完成")
        click.echo(f"  成功: {success_count}/{len(files)}")
        click.echo(f"  失败: {fail_count}/{len(files)}")
        if fail_count > 0:
            click.echo("\n失败文件列表:")
            for r in results:
                if r['status'] == 'failed':
                    click.echo(f"  - {r['file']}: {r.get('error', '未知错误')}")
        click.echo('='*60)
    
    if fail_count > 0:
        sys.exit(1)
    else:
        click.echo("\n[SUCCESS] 所有文件处理完成！")


@cli.group()
def draft():
    """草稿管理命令"""
    pass


@draft.command('list')
@click.option('--offset', default=0, help='偏移量')
@click.option('--count', default=20, help='返回数量（1-20）')
def list_drafts(offset, count):
    """列出草稿箱中的文章"""
    try:
        api = WeChatAPI()
        drafts = api.list_drafts(offset=offset, count=count)
        
        if not drafts:
            click.echo("草稿箱为空")
            return
        
        click.echo(f"\n{'Media ID':<30} {'标题':<40} {'更新时间'}")
        click.echo("-" * 100)
        
        for item in drafts:
            media_id = item.get('media_id', '')[:28]
            content = item.get('content', {})
            news_item = content.get('news_item', [{}])[0]
            title = news_item.get('title', '')[:38]
            update_time = item.get('update_time', '')
            
            click.echo(f"{media_id:<30} {title:<40} {update_time}")
        
        click.echo()
        
    except WeChatAPIError as e:
        click.echo(f"[ERROR] 微信 API 错误: {e}", err=True)
        sys.exit(1)


@draft.command('get')
@click.argument('media_id')
def get_draft(media_id):
    """获取草稿详情"""
    try:
        api = WeChatAPI()
        draft_data = api.get_draft(media_id)
        
        content = draft_data.get('content', {})
        news_item = content.get('news_item', [{}])[0]
        
        click.echo(f"\n[FILE] 草稿详情")
        click.echo(f"Media ID: {media_id}")
        click.echo(f"标题: {news_item.get('title', '')}")
        click.echo(f"作者: {news_item.get('author', '')}")
        click.echo(f"摘要: {news_item.get('digest', '')}")
        click.echo(f"原文链接: {news_item.get('content_source_url', '')}")
        click.echo()
        
    except WeChatAPIError as e:
        click.echo(f"[ERROR] 微信 API 错误: {e}", err=True)
        sys.exit(1)


@draft.command('delete')
@click.argument('media_id')
@click.confirmation_option(prompt='确定要删除这个草稿吗？')
def delete_draft(media_id):
    """删除草稿"""
    try:
        api = WeChatAPI()
        success = api.delete_draft(media_id)
        
        if success:
            click.echo(f"[OK] 草稿 {media_id} 已删除")
        else:
            click.echo(f"[ERROR] 删除失败", err=True)
            sys.exit(1)
            
    except WeChatAPIError as e:
        click.echo(f"[ERROR] 微信 API 错误: {e}", err=True)
        sys.exit(1)


@cli.command('serve')
@click.argument('file', type=click.Path(exists=True))
@click.option('-p', '--port', default=8080, help='服务器端口（默认 8080）')
@click.option('--host', default='0.0.0.0', help='绑定地址（默认 0.0.0.0，允许所有接口访问）')
@click.option('--theme', default='default', help='使用主题')
@click.option('--open', 'auto_open', is_flag=True, help='自动打开浏览器（服务器环境无效）')
def serve_file(file, port, host, theme, auto_open):
    """
    启动临时 HTTP 服务器预览 Markdown 文件
    
    适用于服务器环境，生成 URL 链接可在浏览器中打开。
    注意：默认绑定 0.0.0.0 允许所有网络接口访问，但需要确保
    防火墙/安全组已开放相应端口，且服务器有公网 IP。
    
    FILE: Markdown 文件路径
    
    示例:
        wechat-publisher serve article.md
        wechat-publisher serve article.md --port 8888 --theme tech
        wechat-publisher serve article.md --host 127.0.0.1  # 仅本地访问
    """
    try:
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        import socketserver
        import threading
        import tempfile
        import webbrowser
        import urllib.request
        
        md_path = Path(file)
        click.echo(f"\n[INFO] 正在准备预览: {md_path}")
        
        # 1. 转换 Markdown
        click.echo(f"[THEME] 使用主题: {theme}")
        converter = MarkdownConverter(theme=theme)
        html_content = converter.convert_file(str(md_path), title=md_path.stem)
        
        # 2. 将图片转为 Base64（确保独立性）
        from src.image_utils import convert_images_to_base64
        click.echo("[BASE64] 正在处理图片...")
        html_content = convert_images_to_base64(html_content, str(md_path.parent))
        click.echo("   ✓ 图片已嵌入")
        
        # 3. 创建临时目录和文件
        temp_dir = tempfile.mkdtemp(prefix='wechat_mp_')
        temp_html = Path(temp_dir) / 'index.html'
        temp_html.write_text(html_content, encoding='utf-8')
        click.echo(f"[FILE] 临时文件已创建")
        
        # 4. 启动 HTTP 服务器
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=temp_dir, **kwargs)
            
            def log_message(self, format, *args):
                # 简化日志输出
                pass
        
        # 尝试启动服务器，如果端口被占用则尝试其他端口
        max_attempts = 10
        current_port = port
        httpd = None
        
        for attempt in range(max_attempts):
            try:
                httpd = HTTPServer((host, current_port), Handler)
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    current_port += 1
                else:
                    raise
        
        if httpd is None:
            click.echo(f"[ERROR] 无法找到可用端口（尝试范围: {port}-{current_port}）", err=True)
            sys.exit(1)
        
        # 获取服务器 URL
        import socket
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "127.0.0.1"
        
        # 尝试获取公网 IP
        public_ip = None
        try:
            public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode('utf-8')
        except:
            pass
        
        click.echo("\n" + "="*60)
        click.echo("[OK] HTTP 服务器已启动!")
        click.echo("="*60)
        click.echo()
        click.echo(f"本地访问: http://localhost:{current_port}")
        click.echo(f"内网访问: http://{local_ip}:{current_port}")
        
        if public_ip and public_ip != local_ip:
            click.echo(f"公网访问: http://{public_ip}:{current_port}")
            click.echo()
            click.echo("[WARN] 公网访问需要确保:")
            click.echo("  1. 防火墙/安全组已开放端口")
            click.echo("  2. 云服务商安全组已放行")
        else:
            click.echo()
            click.echo("[WARN] 无法获取公网 IP，可能的原因:")
            click.echo("  1. 服务器在内网/无公网 IP")
            click.echo("  2. 需要使用内网穿透工具（如 ngrok）")
            click.echo()
            click.echo("[TIP] 推荐使用 'copy' 命令生成独立 HTML 文件:")
            click.echo(f"  wechat-publisher copy {file}")
        click.echo()
        click.echo("提示:")
        click.echo("  - 在飞书或其他平台中可以直接访问上述链接")
        click.echo("  - 按 Ctrl+C 停止服务器")
        click.echo("="*60)
        
        # 尝试自动打开浏览器（仅在非服务器环境有效）
        if auto_open:
            try:
                webbrowser.open(f'http://localhost:{current_port}')
            except:
                pass
        
        # 启动服务器
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\n[INFO] 服务器已停止")
            httpd.shutdown()
            
    except Exception as e:
        click.echo(f"[ERROR] 错误: {e}", err=True)
        sys.exit(1)


@cli.group()
def config_cmd():
    """配置管理命令"""
    pass


@config_cmd.command('init')
def init_config():
    """初始化配置文件"""
    click.echo("[CONFIG] 初始化配置\n")
    
    # 检查是否已存在配置
    if config.config_file.exists():
        if not click.confirm("配置文件已存在，是否覆盖？"):
            click.echo("已取消")
            return
    
    # 输入配置
    appid = click.prompt("请输入微信公众号 AppID", default=config.get_appid() or "")
    appsecret = click.prompt("请输入微信公众号 AppSecret", default=config.get_appsecret() or "", hide_input=True)
    author = click.prompt("请输入默认作者名称", default=config.get("default.author", ""))
    
    # 保存配置
    config.init_config(appid=appid, appsecret=appsecret, author=author)
    
    click.echo(f"\n[OK] 配置已保存到: {config.config_file}")
    click.echo("   您也可以通環境变量 WECHAT_APPID 和 WECHAT_APPSECRET 设置")


@config_cmd.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key, value):
    """设置配置项"""
    config.set(key, value)
    click.echo(f"[OK] 已设置 {key} = {value}")


@config_cmd.command('get')
@click.argument('key')
def get_config(key):
    """获取配置项"""
    value = config.get(key)
    if value is not None:
        click.echo(f"{key} = {value}")
    else:
        click.echo(f"配置项 {key} 不存在")


@config_cmd.command('list')
def list_config():
    """列出所有配置"""
    click.echo("\n当前配置:")
    click.echo(json.dumps(config._config, indent=2, ensure_ascii=False))


@config_cmd.command('logs')
@click.option('--lines', '-n', default=50, help='显示的行数')
@click.option('--level', '-l', help='过滤日志级别 (DEBUG/INFO/WARNING/ERROR)')
def show_logs(lines, level):
    """查看日志文件"""
    from src.logger import logger_manager
    
    log_file = logger_manager.log_dir / "app.log"
    
    if not log_file.exists():
        click.echo("[WARN] 日志文件不存在")
        return
    
    # 读取日志文件
    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    # 按级别过滤
    if level:
        level = level.upper()
        filtered_lines = [l for l in all_lines if f"[{level}]" in l]
    else:
        filtered_lines = all_lines
    
    # 显示最后 N 行
    display_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines
    
    click.echo(f"\n[LOG] 显示最近 {len(display_lines)} 行日志")
    if level:
        click.echo(f"[LOG] 级别过滤: {level}")
    click.echo("-" * 60)
    for line in display_lines:
        click.echo(line.rstrip())
    click.echo("-" * 60)


@config_cmd.command('clear-logs')
@click.confirmation_option(prompt='确定要清空所有日志文件吗？')
def clear_logs():
    """清空日志文件"""
    from src.logger import logger_manager
    
    log_dir = logger_manager.log_dir
    if not log_dir.exists():
        click.echo("[WARN] 日志目录不存在")
        return
    
    # 清空所有 .log 文件
    cleared = 0
    for log_file in log_dir.glob("*.log"):
        log_file.write_text('', encoding='utf-8')
        cleared += 1
    
    click.echo(f"[OK] 已清空 {cleared} 个日志文件")


@cli.group()
def theme():
    """主题管理命令"""
    pass


@theme.command('list')
def list_themes():
    """列出可用主题"""
    from src.theme_manager import ThemeManager
    
    manager = ThemeManager()
    themes = manager.list_themes()
    
    click.echo("\nTHEME: 可用主题列表:")
    click.echo()
    
    # 内置主题
    click.echo("[BUILTIN] 内置主题:")
    builtin_themes = [t for t in themes if t['type'] == 'builtin']
    for theme in builtin_themes:
        click.echo(f"  - {theme['name']:<12} - {theme['description']}")
    
    # 自定义主题
    custom_themes = [t for t in themes if t['type'] == 'custom']
    if custom_themes:
        click.echo("\n[CUSTOM]  自定义主题:")
        for theme in custom_themes:
            extra = ""
            if 'author' in theme:
                extra = f" by {theme['author']}"
            if 'version' in theme:
                extra += f" v{theme['version']}"
            click.echo(f"  - {theme['name']:<12} - {theme['description']}{extra}")
    
    click.echo(f"\n[TIP] 使用 'theme create <name>' 创建新主题")
    click.echo(f"[TIP] 使用 'theme preview <name> --gui' 预览主题效果")
    click.echo()


@theme.command('create')
@click.argument('name')
@click.option('--dir', type=click.Path(), help='指定保存目录（默认保存在用户配置目录）')
@click.option('--local', is_flag=True, help='保存到当前目录的 .themes 文件夹')
def create_theme(name, dir, local):
    """创建新主题（交互式）"""
    from src.theme_manager import ThemeManager, ThemeConfig
    
    # 确定保存目录
    if local:
        save_dir = Path('.themes')
    elif dir:
        save_dir = Path(dir)
    else:
        save_dir = None  # 使用默认目录
    
    manager = ThemeManager()
    
    click.echo(f"\nTHEME: 创建新主题: {name}\n")
    
    # 检查名称
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        click.echo("[ERROR] 主题名称只能包含字母、数字、下划线和横线", err=True)
        sys.exit(1)
    
    if name in manager.BUILTIN_THEMES:
        click.echo(f"[ERROR] '{name}' 是内置主题名称，请使用其他名称", err=True)
        sys.exit(1)
    
    # 交互式输入配置
    description = click.prompt("主题描述", default="自定义主题")
    author = click.prompt("作者名称", default="")
    
    click.echo("\n颜色配置（支持 #RRGGBB 格式）:")
    primary_color = click.prompt("主色调", default="#07c160")
    text_color = click.prompt("正文颜色", default="#333333")
    heading_color = click.prompt("标题颜色", default="#000000")
    bg_color = click.prompt("背景颜色", default="#ffffff")
    link_color = click.prompt("链接颜色", default=primary_color)
    
    click.echo("\n字体配置:")
    font_size = click.prompt("字体大小", default="16px")
    line_height = click.prompt("行高", default="1.8")
    
    # 创建配置
    theme_config = ThemeConfig(
        name=name,
        description=description,
        author=author,
        primary_color=primary_color,
        text_color=text_color,
        heading_color=heading_color,
        bg_color=bg_color,
        link_color=link_color,
        font_size=font_size,
        line_height=line_height
    )
    
    try:
        theme_path = manager.create_theme(name, theme_config, save_dir=save_dir)
        click.echo(f"\n[OK] 主题已创建: {theme_path}")
        
        # 提示如何使用
        if save_dir:
            click.echo(f"\n[TIP] 主题保存在当前目录，使用时需要指定路径:")
            click.echo(f"  wechat-publisher convert article.md --theme {theme_path}")
        else:
            click.echo(f"\n[TIP] 使用以下命令预览主题:")
            click.echo(f"  wechat-publisher theme preview {name}")
    except ValueError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)


@theme.command('preview')
@click.argument('theme_name')
@click.option('-o', '--output', default='theme_preview.html', help='输出文件')
@click.option('--gui', is_flag=True, help='使用 GUI 窗口预览')
def preview_theme(theme_name, output, gui):
    """预览主题效果"""
    # 创建示例内容
    sample_md = """# 主题预览

这是一级标题

这是一段普通文本，**这是粗体**，*这是斜体*，~~这是删除线~~。

## 二级标题

> 这是一段引用文本，用于展示引用块的样式。

### 三级标题

- 列表项 1
- 列表项 2
- 列表项 3

1. 有序列表 1
2. 有序列表 2
3. 有序列表 3

```python
def hello():
    print("Hello, World!")
```

| 表头 1 | 表头 2 |
|--------|--------|
| 内容 1 | 内容 2 |
| 内容 3 | 内容 4 |

---

[链接文字](https://example.com)
"""
    
    try:
        converter = MarkdownConverter(theme=theme_name)
        html = converter.convert(sample_md)
        
        if gui:
            # GUI 预览
            from src.preview_gui import preview_with_copy
            preview_with_copy(html, ".", title=f"主题预览: {theme_name}", convert_images=False)
        else:
            # 保存到文件
            Path(output).write_text(html, encoding='utf-8')
            click.echo(f"[OK] 主题预览已保存: {output}")
        
    except Exception as e:
        click.echo(f"[ERROR] 预览生成失败: {e}", err=True)
        sys.exit(1)


@theme.command('delete')
@click.argument('name')
@click.confirmation_option(prompt='确定要删除这个主题吗？')
def delete_theme(name):
    """删除自定义主题"""
    from src.theme_manager import ThemeManager
    
    manager = ThemeManager()
    
    try:
        if manager.delete_theme(name):
            click.echo(f"[OK] 主题 '{name}' 已删除")
        else:
            click.echo(f"[WARN] 主题 '{name}' 不存在")
    except ValueError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)


@theme.command('export')
@click.argument('name')
@click.argument('output', type=click.Path(), required=False)
def export_theme(name, output):
    """导出主题"""
    from src.theme_manager import ThemeManager
    
    manager = ThemeManager()
    
    if not output:
        output = f"{name}.theme.css"
    
    try:
        path = manager.export_theme(name, output)
        click.echo(f"[OK] 主题已导出: {path}")
    except Exception as e:
        click.echo(f"[ERROR] 导出失败: {e}", err=True)
        sys.exit(1)


@theme.command('import')
@click.argument('css_file', type=click.Path(exists=True))
@click.option('--name', help='指定主题名称（默认使用文件名）')
def import_theme(css_file, name):
    """导入外部 CSS 文件作为主题"""
    from src.theme_manager import ThemeManager
    
    manager = ThemeManager()
    
    try:
        theme_path = manager.import_theme(css_file, name)
        click.echo(f"[OK] 主题已导入: {theme_path}")
        click.echo(f"\n您可以通过以下命令预览:")
        theme_name = Path(theme_path).stem
        click.echo(f"  wechat-mp-publisher theme preview {theme_name} --gui")
    except Exception as e:
        click.echo(f"[ERROR] 导入失败: {e}", err=True)
        sys.exit(1)


@theme.command('edit')
@click.argument('name')
def edit_theme(name):
    """编辑自定义主题配置（交互式）"""
    from src.theme_manager import ThemeManager, ThemeConfig
    from src.config import config as app_config
    import json
    
    manager = ThemeManager()
    
    # 检查是否是自定义主题
    if name in manager.BUILTIN_THEMES:
        click.echo(f"[ERROR] 不能编辑内置主题 '{name}'", err=True)
        click.echo("[TIP] 您可以先创建一个继承此主题的新主题:")
        click.echo(f"  theme create my_{name}")
        sys.exit(1)
    
    # 读取现有配置
    config_path = app_config.config_dir / "themes" / f"{name}.json"
    css_path = app_config.config_dir / "themes" / f"{name}.css"
    
    if not config_path.exists():
        # 如果没有配置文件，但有 CSS 文件，创建一个默认配置
        if css_path.exists():
            click.echo(f"[WARN] 主题 '{name}' 没有配置文件，将创建默认配置")
            current_config = ThemeConfig(
                name=name,
                description="自定义主题",
                author=""
            )
        else:
            click.echo(f"[ERROR] 主题 '{name}' 不存在", err=True)
            sys.exit(1)
    else:
        # 读取现有配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            current_config = ThemeConfig(**config_data)
        except Exception as e:
            click.echo(f"[ERROR] 读取配置文件失败: {e}", err=True)
            sys.exit(1)
    
    click.echo(f"\n编辑主题: {name}")
    click.echo("直接按回车保持原值不变\n")
    
    # 编辑基本配置
    description = click.prompt("主题描述", default=current_config.description)
    author = click.prompt("作者名称", default=current_config.author)
    
    click.echo("\n颜色配置（支持 #RRGGBB 格式）:")
    primary_color = click.prompt("主色调", default=current_config.primary_color)
    text_color = click.prompt("正文颜色", default=current_config.text_color)
    heading_color = click.prompt("标题颜色", default=current_config.heading_color)
    bg_color = click.prompt("背景颜色", default=current_config.bg_color)
    link_color = click.prompt("链接颜色", default=current_config.link_color)
    
    click.echo("\n字体配置:")
    font_size = click.prompt("字体大小", default=current_config.font_size)
    line_height = click.prompt("行高", default=current_config.line_height)
    
    # 确认保存
    click.echo("\n修改内容:")
    if description != current_config.description:
        click.echo(f"  描述: {current_config.description} -> {description}")
    if author != current_config.author:
        click.echo(f"  作者: {current_config.author} -> {author}")
    if primary_color != current_config.primary_color:
        click.echo(f"  主色调: {current_config.primary_color} -> {primary_color}")
    
    if not click.confirm("\n是否保存修改？"):
        click.echo("已取消")
        return
    
    # 创建新配置
    new_config = ThemeConfig(
        name=name,
        description=description,
        author=author,
        primary_color=primary_color,
        text_color=text_color,
        heading_color=heading_color,
        bg_color=bg_color,
        link_color=link_color,
        font_size=font_size,
        line_height=line_height
    )
    
    # 重新生成 CSS
    try:
        css_content = manager._generate_css(new_config)
        css_path.write_text(css_content, encoding='utf-8')
        
        # 更新配置文件
        config_dict = {
            'name': name,
            'description': description,
            'author': author,
            'version': current_config.version,
            'primary_color': primary_color,
            'text_color': text_color,
            'heading_color': heading_color,
            'bg_color': bg_color,
            'link_color': link_color,
            'font_size': font_size,
            'line_height': line_height
        }
        config_path.write_text(json.dumps(config_dict, indent=2, ensure_ascii=False), encoding='utf-8')
        
        click.echo(f"\n[OK] 主题 '{name}' 已更新")
        click.echo(f"[TIP] 使用 'theme preview {name} --gui' 预览效果")
        
    except Exception as e:
        click.echo(f"[ERROR] 保存失败: {e}", err=True)
        sys.exit(1)


@cli.command('copy')
@click.argument('file', type=click.Path(exists=True))
@click.option('--theme', default='default', help='使用主题')
@click.option('-o', '--output', type=click.Path(), help='输出 HTML 文件路径')
@click.option('--no-clipboard', is_flag=True, help='不尝试复制到剪贴板')
def copy_article(file, theme, output, no_clipboard):
    """
    生成可复制的内容（适合服务器环境）
    
    将 Markdown 转换为带 Base64 图片的完整 HTML，可直接复制使用
    
    FILE: Markdown 文件路径
    
    示例:
        wechat-publisher copy article.md
        wechat-publisher copy article.md --theme tech -o output.html
    """
    try:
        md_path = Path(file)
        click.echo(f"\n[INFO] 正在处理: {md_path}")
        
        # 1. 转换 Markdown
        click.echo(f"[THEME] 使用主题: {theme}")
        converter = MarkdownConverter(theme=theme)
        html_content = converter.convert_file(str(md_path), title=md_path.stem)
        
        # 2. 将图片转为 Base64
        from src.image_utils import convert_images_to_base64
        click.echo("[BASE64] 正在处理图片...")
        html_content = convert_images_to_base64(html_content, str(md_path.parent))
        click.echo("   ✓ 图片已嵌入 HTML")
        
        # 3. 保存 HTML 文件
        output_path = Path(output) if output else Path(f"{md_path.stem}_copy.html")
        output_path.write_text(html_content, encoding='utf-8')
        
        file_size = output_path.stat().st_size
        click.echo(f"[OK] HTML 文件已保存: {output_path}")
        click.echo(f"   文件大小: {file_size / 1024:.1f} KB")
        
        # 4. 尝试复制到剪贴板（如果环境支持）
        if not no_clipboard:
            try:
                import pyperclip
                pyperclip.copy(html_content)
                click.echo("[OK] 内容已复制到剪贴板")
                click.echo("   提示: 可以直接粘贴到公众号编辑器")
            except Exception as e:
                click.echo(f"[WARN] 无法复制到剪贴板: {e}")
                click.echo("   提示: HTML 文件已保存，请手动打开并复制")
        
        click.echo("\n" + "="*60)
        click.echo("使用建议:")
        click.echo("  1. 在飞书: 可以直接发送 HTML 文件")
        click.echo("  2. 在公众号: 用浏览器打开 HTML 文件，全选复制")
        click.echo("  3. 其他平台: 使用生成的 HTML 文件内容")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"[ERROR] 错误: {e}", err=True)
        sys.exit(1)


@cli.command('preview-gui')
@click.argument('file', type=click.Path(exists=True))
@click.option('--theme', default='default', help='使用主题（default/tech/minimal/elegant）')
@click.option('--no-convert-images', is_flag=True, help='不转换图片为 Base64（复制时图片可能无法显示）')
def preview_gui(file, theme, no_convert_images):
    """
    打开 GUI 预览窗口，支持一键复制到公众号编辑器
    
    此命令会将 Markdown 转换为 HTML，并在 GUI 窗口中预览。
    点击"复制全部内容"按钮后，可以直接粘贴到公众号编辑器。
    
    默认会将本地图片转换为 Base64 编码，确保复制后图片能正常显示。
    
    FILE: Markdown 文件路径
    
    示例:
        wechat-publisher preview-gui article.md
        wechat-publisher preview-gui article.md --theme tech
    """
    try:
        from src.preview_gui import preview_with_copy
        from src.converter import MarkdownConverter
        
        click.echo(f"📖 正在读取文件: {file}")
        md_path = Path(file)
        
        # 转换 Markdown
        click.echo(f"THEME: 正在转换（主题: {theme}）...")
        converter = MarkdownConverter(theme=theme)
        html_content = converter.convert_file(str(md_path), title=md_path.stem)
        
        # 打开 GUI 预览
        click.echo("🖥️  正在打开预览窗口...")
        click.echo('   提示: 点击窗口右上角的"复制全部内容"按钮，即可复制到公众号编辑器')
        
        preview_with_copy(
            html_content=html_content,
            base_path=str(md_path.parent),
            title=f"预览: {md_path.name}",
            convert_images=not no_convert_images
        )
        
        click.echo("[OK] 预览窗口已关闭")
        
    except ImportError as e:
        click.echo(f"[ERROR] 缺少依赖: {e}", err=True)
        click.echo("请安装 GUI 依赖: pip install pywebview pyperclip", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[ERROR] 错误: {e}", err=True)
        sys.exit(1)


def main():
    """主入口"""
    cli(auto_envvar_prefix='WECHAT')


if __name__ == '__main__':
    main()
