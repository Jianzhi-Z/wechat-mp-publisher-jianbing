#!/usr/bin/env python3
"""
验证 Skill 完整性
检查所有必需文件和配置
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """检查文件是否存在"""
    if Path(path).exists():
        print(f"[OK] {description}: {path}")
        return True
    else:
        print(f"[MISSING] {description}: {path}")
        return False

def check_directory(path, description):
    """检查目录是否存在"""
    if Path(path).is_dir():
        print(f"[OK] {description}: {path}")
        return True
    else:
        print(f"[MISSING] {description}: {path}")
        return False

def main():
    """验证 Skill"""
    print("=" * 60)
    print("WeChat MP Publisher Skill Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 必需文件
    print("[Required Files]")
    required_files = [
        ("SKILL.md", "OpenClaw Skill description"),
        ("README.md", "User documentation"),
        ("LICENSE", "License file"),
        ("setup.py", "setuptools config"),
        ("pyproject.toml", "Modern packaging config"),
        ("MANIFEST.in", "Package manifest"),
        ("requirements.txt", "Dependencies"),
    ]
    
    for path, desc in required_files:
        if not check_file(path, desc):
            all_ok = False
    
    print()
    
    # 推荐文件
    print("[Recommended Files]")
    recommended_files = [
        ("AGENTS.md", "Agent guide"),
        ("PACKAGING.md", "Packaging guide"),
    ]
    
    for path, desc in recommended_files:
        check_file(path, desc)
    
    print()
    
    # 源代码目录
    print("[Source Code]")
    required_dirs = [
        ("src", "Source directory"),
        ("themes", "Themes directory"),
        ("tests", "Tests directory"),
    ]
    
    for path, desc in required_dirs:
        if not check_directory(path, desc):
            all_ok = False
    
    print()
    
    # 检查核心源文件
    print("[Core Modules]")
    core_modules = [
        "src/__init__.py",
        "src/cli.py",
        "src/converter.py",
        "src/config.py",
        "src/logger.py",
        "src/theme_manager.py",
        "src/uploader.py",
        "src/wechat_api.py",
        "src/image_utils.py",
        "src/preview_gui.py",
    ]
    
    for module in core_modules:
        if not check_file(module, f"Module {Path(module).stem}"):
            all_ok = False
    
    print()
    
    # 检查主题文件
    print("[Built-in Themes]")
    themes = [
        "themes/default.css",
        "themes/tech.css",
        "themes/minimal.css",
        "themes/elegant.css",
    ]
    
    for theme in themes:
        if not check_file(theme, f"Theme {Path(theme).stem}"):
            all_ok = False
    
    print()
    
    # 检查测试文件
    print("[Test Files]")
    tests = [
        "tests/__init__.py",
        "tests/test_config.py",
        "tests/test_converter.py",
        "tests/test_uploader.py",
    ]
    
    for test in tests:
        check_file(test, f"Test {Path(test).stem}")
    
    print()
    
    # 检查版本一致性
    print("[Version Check]")
    try:
        from src import __version__
        print(f"[OK] Source version: {__version__}")
        
        # 检查 pyproject.toml
        try:
            import tomllib
            with open("pyproject.toml", "rb") as f:
                pyproject = tomllib.load(f)
                pyproject_version = pyproject.get("project", {}).get("version")
                if pyproject_version == __version__:
                    print(f"[OK] pyproject.toml version: {pyproject_version}")
                else:
                    print(f"[MISMATCH] pyproject.toml version: {pyproject_version} != {__version__}")
                    all_ok = False
        except ImportError:
            # Python < 3.11
            print("[SKIP] Cannot import tomllib (Python < 3.11)")
    except Exception as e:
        print(f"[WARN] Version check failed: {e}")
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("[SUCCESS] Skill verification passed!")
        return 0
    else:
        print("[FAILED] Skill verification failed, please check missing items")
        return 1

if __name__ == "__main__":
    sys.exit(main())
