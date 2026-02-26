#!/usr/bin/env python3
"""
简单的测试运行脚本 - 小白友好版
直接运行这个文件即可执行所有测试
"""

import sys
import subprocess

def main():
    """运行测试"""
    print("=" * 60)
    print("WeChat MP Publisher 测试运行器")
    print("=" * 60)
    print()
    
    # 检查 pytest 是否安装
    try:
        import pytest
        print("[OK] pytest 已安装")
    except ImportError:
        print("[INSTALL] pytest 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "-q"])
        print("[OK] pytest 安装完成")
    
    print()
    print("开始运行测试...")
    print("-" * 60)
    
    # 运行测试
    try:
        # 使用 pytest 运行测试
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            cwd=".",
            capture_output=False
        )
        
        print()
        print("-" * 60)
        
        if result.returncode == 0:
            print("[SUCCESS] 所有测试通过！")
            return 0
        else:
            print("[FAILED] 有测试失败，请查看上面的错误信息")
            return 1
            
    except Exception as e:
        print(f"[ERROR] 运行测试时出错: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
