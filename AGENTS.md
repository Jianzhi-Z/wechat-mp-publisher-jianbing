# WeChat MP Publisher - Agent 使用指南

本文档面向 AI Agent，提供项目的快速理解和使用指引。

## 项目概述

**WeChat MP Publisher** 是一个将 Markdown 转换为微信公众号格式的命令行工具。

**版本**: v1.1.0  
**状态**: 稳定可用，30个测试通过  
**适用场景**: 需要将 Markdown 文章发布到微信公众号的用户

## 快速理解

### 核心能力

```
Markdown → HTML + CSS → 微信草稿箱
     ↓           ↓
  解析器      主题系统
  代码高亮    图片处理
  表格转换    批量转换
```

### 三种使用模式

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| API 发布 | `convert --draft` | 认证服务号 |
| GUI 复制 | `preview-gui` | 有图形界面的环境 |
| 服务器复制 | `copy` / `serve` | OpenClaw/服务器环境 |

## Agent 常用命令

### 基础转换

```bash
# 转换单个文件
wechat-publisher convert article.md --preview

# 使用主题
wechat-publisher convert article.md --theme tech --preview

# 批量转换
wechat-publisher convert articles/*.md --preview --output-dir output/
```

### GUI 模式（最常用）

```bash
# 打开 GUI 窗口（适合未认证公众号）
wechat-publisher preview-gui article.md --theme tech
```

### 服务器环境（OpenClaw/无 GUI）

```bash
# 方式 1：生成可复制的内容（推荐）
wechat-publisher copy article.md --theme tech

# 方式 2：启动 HTTP 服务器
wechat-publisher serve article.md --port 8080

# 方式 3：生成独立 HTML
wechat-publisher convert article.md --base64 --preview
```

**特点：**
- `copy`：生成 Base64 嵌入的独立 HTML，可复制到剪贴板
- `serve`：启动临时 HTTP 服务器，提供访问链接
- `--base64`：`convert` 选项，生成独立 HTML 文件

### 主题管理

```bash
# 列出主题
wechat-publisher theme list

# 创建主题
wechat-publisher theme create mytheme

# 使用本地主题
wechat-publisher convert article.md --theme .themes/mytheme.css
```

## 项目结构

```
src/
├── cli.py           # CLI 入口，所有命令定义
├── converter.py     # Markdown → HTML 核心
├── config.py        # 配置管理 (~/.wechat-mp-publisher/)
├── logger.py        # 日志系统
├── theme_manager.py # 主题管理
├── uploader.py      # 图片上传处理
├── wechat_api.py    # 微信 API 封装
├── image_utils.py   # 图片压缩、Base64
└── preview_gui.py   # GUI 窗口

themes/              # 内置主题 CSS
tests/               # 30个测试
examples/            # 使用示例
```

## 配置信息

**配置文件位置**: `~/.wechat-mp-publisher/config.json`

**必需配置**:
- `wechat.appid` - 微信公众号 AppID
- `wechat.appsecret` - 微信公众号 AppSecret

**可选配置**:
- `default.author` - 默认作者
- `default.theme` - 默认主题

## 开发指南

### 运行测试

```bash
pytest tests/ -v
```

### 添加新功能

1. CLI 命令: 在 `src/cli.py` 中添加
2. 核心功能: 在对应模块实现
3. 测试: 在 `tests/` 添加测试用例

### 调试

```bash
# 查看日志
wechat-publisher config logs --level DEBUG

# 调试模式
wechat-publisher --debug convert article.md --preview
```

## 常见问题（Agent 须知）

### Q: 用户是未认证订阅号怎么办？
A: 推荐使用 `preview-gui` 命令，打开 GUI 窗口后一键复制到公众号编辑器。

### Q: 图片上传失败？
A: 检查：
1. 图片格式（JPG/PNG/GIF/BMP）
2. 图片大小（>500KB 会自动压缩）
3. Token 是否过期

### Q: 如何创建自定义主题？
A: 
```bash
wechat-publisher theme create mytheme
# 交互式输入颜色、字体等配置
```

## 依赖项

**运行时必需**: markdown, beautifulsoup4, pygments, requests, click, pyyaml, pillow, pywebview, pyperclip

**开发可选**: pytest, black, flake8

## 更新记录

- **v1.1.0**: 批量转换、图片压缩、错误重试、日志系统
- **v1.0.0**: GUI 预览、主题管理
- **v0.1.0**: 基础转换、草稿发布
