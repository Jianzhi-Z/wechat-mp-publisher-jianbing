#!/usr/bin/env python3
"""
微信公众号文章发布工具
将 Markdown 转换为微信公众号格式并保存到草稿箱
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wechat-mp-publisher",
    version="1.1.0",
    author="OpenClaw Community",
    author_email="",
    description="将 Markdown 文章转换并发布到微信公众号草稿箱",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/wechat-mp-publisher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "wechat-publisher=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.css", "*.html", "*.yaml", "*.json"],
    },
)
