#!/usr/bin/env python3
"""
图片处理工具模块
提供图片转 Base64、压缩等功能
"""

import base64
import io
from pathlib import Path
from typing import Optional
from PIL import Image


def image_to_base64(image_path: str) -> Optional[str]:
    """
    将本地图片转换为 Base64 Data URL
    
    Args:
        image_path: 本地图片路径
        
    Returns:
        Base64 Data URL，如：data:image/jpeg;base64,/9j/4AAQ...
        如果转换失败返回 None
    """
    try:
        path = Path(image_path)
        if not path.exists():
            print(f"图片不存在: {image_path}")
            return None
        
        # 检查文件大小（超过 2MB 提示警告）
        file_size = path.stat().st_size
        if file_size > 2 * 1024 * 1024:
            print(f"警告: 图片 {path.name} 超过 2MB，可能影响复制性能")
        
        # 读取图片二进制数据
        with open(path, 'rb') as f:
            image_data = f.read()
        
        # 获取图片格式
        suffix = path.suffix.lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }.get(suffix, 'image/jpeg')
        
        # 转换为 Base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_data}"
        
        return data_url
        
    except Exception as e:
        print(f"图片转 Base64 失败 {image_path}: {e}")
        return None


def compress_image(image_path: str, max_width: int = 1080, quality: int = 85) -> Optional[str]:
    """
    压缩图片并返回压缩后的临时文件路径
    
    Args:
        image_path: 原始图片路径
        max_width: 最大宽度
        quality: JPEG 质量
        
    Returns:
        压缩后的图片路径，如果不需要压缩则返回原路径
    """
    try:
        path = Path(image_path)
        
        # 打开图片
        with Image.open(image_path) as img:
            # 转换为 RGB（如果是 RGBA 或 P 模式）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # 如果宽度超过限制，进行缩放
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 检查是否需要压缩（文件大于 500KB）
            file_size = path.stat().st_size
            if file_size <= 500 * 1024 and img.width <= max_width:
                # 不需要压缩
                return str(path)
            
            # 保存到临时文件
            temp_dir = Path.home() / ".wechat-mp-publisher" / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            temp_path = temp_dir / f"compressed_{path.stem}.jpg"
            img.save(temp_path, 'JPEG', quality=quality, optimize=True)
            
            return str(temp_path)
            
    except Exception as e:
        print(f"压缩图片失败 {image_path}: {e}")
        return image_path  # 返回原路径


def convert_images_to_base64(html: str, base_path: str = ".", compress: bool = True) -> str:
    """
    将 HTML 中的所有本地图片转换为 Base64 Data URL
    
    Args:
        html: 原始 HTML
        base_path: 基础路径（用于解析相对路径）
        compress: 是否先压缩图片
        
    Returns:
        转换后的 HTML
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, 'html.parser')
    base = Path(base_path)
    
    converted_count = 0
    failed_count = 0
    
    for img in soup.find_all('img'):
        src = img.get('src', '')
        
        # 跳过已经是 Data URL 或远程 URL 的图片
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            continue
        
        try:
            # 解析本地图片路径
            if src.startswith('./') or src.startswith('../'):
                image_path = base / src
            elif src.startswith('/'):
                image_path = Path(src)
            else:
                image_path = base / src
            
            image_path = image_path.resolve()
            
            if not image_path.exists():
                print(f"图片不存在，跳过: {src}")
                failed_count += 1
                continue
            
            # 可选：先压缩图片
            if compress:
                process_path = compress_image(str(image_path))
            else:
                process_path = str(image_path)
            
            # 转换为 Base64
            data_url = image_to_base64(process_path)
            
            if data_url:
                img['src'] = data_url
                # 保留原始路径作为 alt 文本（方便调试）
                if not img.get('alt'):
                    img['alt'] = src
                converted_count += 1
                
                # 清理临时压缩文件
                if process_path != str(image_path) and Path(process_path).exists():
                    Path(process_path).unlink()
            else:
                failed_count += 1
                
        except Exception as e:
            print(f"处理图片失败 {src}: {e}")
            failed_count += 1
    
    print(f"图片转换完成: {converted_count} 成功, {failed_count} 失败")
    return str(soup)


def get_image_info(image_path: str) -> dict:
    """
    获取图片信息
    
    Args:
        image_path: 图片路径
        
    Returns:
        图片信息字典
    """
    try:
        path = Path(image_path)
        
        with Image.open(image_path) as img:
            info = {
                'path': str(path),
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'size_bytes': path.stat().st_size,
                'size_mb': round(path.stat().st_size / (1024 * 1024), 2)
            }
        return info
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    # 测试
    import sys
    
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        print(f"测试图片: {test_path}")
        
        # 显示图片信息
        info = get_image_info(test_path)
        print(f"图片信息: {info}")
        
        # 转换为 Base64
        data_url = image_to_base64(test_path)
        if data_url:
            print(f"转换成功，长度: {len(data_url)} 字符")
            print(f"前 100 字符: {data_url[:100]}...")
        else:
            print("转换失败")
    else:
        print("用法: python image_utils.py <图片路径>")
