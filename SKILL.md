---
name: wechat-mp-publisher
description: 将 Markdown 文章转换并发布到微信公众号草稿箱，支持多主题样式、批量处理、图片自动压缩和 GUI 预览复制。
metadata:
  openclaw:
    emoji: "📝"
    requires:
      bins: ["wechat-publisher"]
      env: ["WECHAT_APPID", "WECHAT_APPSECRET"]
---

# WeChat MP Publisher

将 Markdown 格式的文章一键转换为微信公众号格式，支持草稿箱发布、批量处理、自定义主题和 GUI 预览复制。

## 功能特性

### 核心功能
- **Markdown 转换** - 支持标准 Markdown 语法，自动转换为微信兼容 HTML
- **图片自动处理** - 自动将本地/远程图片上传到微信素材库，支持自动压缩
- **批量转换** - 支持多个文件或整个目录批量处理
- **多主题样式** - 内置 4 种主题，支持自定义 CSS
- **草稿管理** - 支持列出、查看、删除草稿
- **GUI 预览** - 可视化预览窗口，支持一键复制到公众号编辑器

### 高级特性
- **错误重试** - API 调用失败自动重试（指数退避策略）
- **日志系统** - 完整的日志记录，便于排查问题
- **Token 自动管理** - 自动获取和刷新 Access Token
- **完全离线** - 不依赖第三方 API 服务

### 版本状态

**当前版本：v1.1.0** ✅

- 30 个自动化测试全部通过
- 支持批量转换和图片压缩
- 支持 GUI 预览和一键复制
- 支持自定义主题管理

---

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourname/wechat-mp-publisher.git
cd wechat-mp-publisher

# 安装依赖
pip install -r requirements.txt

# 安装命令行工具
pip install -e .
```

---

## 配置

### 方式 1：命令行初始化（推荐）

```bash
wechat-publisher config init
```

根据提示输入：
- **AppID** - 微信公众号开发者 ID
- **AppSecret** - 微信公众号开发者密码
- **默认作者** - 文章默认作者名称

### 方式 2：环境变量

```bash
export WECHAT_APPID=wx1234567890abcdef
export WECHAT_APPSECRET=your_app_secret_here
```

### 方式 3：手动配置

```bash
# 设置配置项
wechat-publisher config set default.author "作者名"
wechat-publisher config set default.theme "tech"
```

---

## 使用方法

### 基础转换

```bash
# 转换 Markdown 并生成本地预览
wechat-publisher convert article.md --preview

# 转换并保存 HTML 文件
wechat-publisher convert article.md -o output.html

# 使用特定主题
wechat-publisher convert article.md --theme tech --preview
```

### 发布到微信草稿箱

```bash
# 基础发布（需要认证服务号）
wechat-publisher convert article.md --draft

# 指定标题和作者
wechat-publisher convert article.md --draft \
  --title "文章标题" \
  --author "作者名"

# 添加封面图片
wechat-publisher convert article.md --draft --cover cover.jpg

# 开启评论
wechat-publisher convert article.md --draft --comment

# 仅粉丝可评论
wechat-publisher convert article.md --draft --comment --fans-comment
```

### 批量转换

```bash
# 转换多个文件
wechat-publisher convert article1.md article2.md --preview

# 转换整个目录
wechat-publisher convert articles/ --preview --output-dir output/

# 批量发布
wechat-publisher convert articles/*.md --draft
```

### GUI 预览与复制

```bash
# 打开 GUI 窗口（适用于所有公众号，包括未认证订阅号）
wechat-publisher preview-gui article.md

# 使用特定主题
wechat-publisher preview-gui article.md --theme tech

# 不转换图片为 Base64
wechat-publisher preview-gui article.md --no-convert-images
```

**GUI 功能说明：**
- 实时预览文章效果
- 点击"复制全部内容"按钮
- 直接粘贴到公众号编辑器
- 图片自动转为 Base64 格式

### 主题管理

```bash
# 列出所有主题
wechat-publisher theme list

# 创建新主题（交互式）
wechat-publisher theme create mytheme

# 创建本地主题（项目专属）
wechat-publisher theme create mytheme --local

# 编辑主题
wechat-publisher theme edit mytheme

# 预览主题
wechat-publisher theme preview mytheme --gui

# 导出主题
wechat-publisher theme export mytheme

# 导入主题
wechat-publisher theme import /path/to/style.css --name mytheme

# 删除主题
wechat-publisher theme delete mytheme
```

### 草稿管理

```bash
# 列出草稿
wechat-publisher draft list

# 查看草稿详情
wechat-publisher draft get <media_id>

# 删除草稿
wechat-publisher draft delete <media_id>
```

### 日志管理

```bash
# 查看日志
wechat-publisher config logs

# 查看错误日志
wechat-publisher config logs --level ERROR

# 查看最近 100 行
wechat-publisher config logs -n 100

# 清空日志
wechat-publisher config clear-logs
```

### 调试模式

```bash
# 详细日志
wechat-publisher -v convert article.md --preview

# 调试模式
wechat-publisher --debug convert article.md --preview
```

---

## 主题定制

### 内置主题

| 主题 | 描述 | 适用场景 |
|------|------|----------|
| `default` | 简洁大方 | 通用文章 |
| `tech` | 代码高亮优化 | 技术文章 |
| `minimal` | 极简风格 | 专注阅读 |
| `elegant` | 文艺气息 | 文学类文章 |

### 创建自定义主题

```bash
# 交互式创建
wechat-publisher theme create mytheme

# 保存到当前目录
wechat-publisher theme create mytheme --local
```

创建后可以编辑 CSS 文件：

```bash
# 编辑全局主题
vim ~/.wechat-mp-publisher/themes/mytheme.css

# 编辑本地主题
vim .themes/mytheme.css
```

### 主题 CSS 示例

```css
.mp-article {
    font-family: "PingFang SC", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
}

.mp-article h1 {
    color: #e74c3c;
    border-bottom: 2px solid #e74c3c;
}

.mp-article blockquote {
    background: #f5f5f5;
    border-left: 4px solid #e74c3c;
}
```

---

## 支持的 Markdown 语法

- **标题** - H1-H6
- **粗体** - `**粗体**`
- **斜体** - `*斜体*`
- **删除线** - `~~删除线~~`
- **列表** - 有序/无序列表
- **链接** - `[文字](url)`
- **图片** - `![描述](路径)`，支持本地和远程
- **引用** - `> 引用内容`
- **代码** - 行内代码和代码块（支持语法高亮）
- **表格** - 标准 Markdown 表格
- **分隔线** - `---`

---

## 技术架构

```
Markdown Input
      ↓
[Converter] - markdown + BeautifulSoup
      ↓
HTML + CSS Theme
      ↓
[Image Processor] - compress & upload
      ↓
[WeChat API] - draft/add
      ↓
WeChat MP Draft
```

### 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| CLI | `cli.py` | 命令行接口 |
| Converter | `converter.py` | Markdown 转 HTML |
| Image Utils | `image_utils.py` | 图片压缩、Base64 |
| Uploader | `uploader.py` | 图片上传处理 |
| WeChat API | `wechat_api.py` | 微信公众号 API |
| Theme Manager | `theme_manager.py` | 主题管理 |
| Logger | `logger.py` | 日志系统 |
| Preview GUI | `preview_gui.py` | GUI 预览窗口 |

---

## 使用限制

### 公众号类型支持

| 功能 | 认证服务号 | 未认证订阅号 |
|------|-----------|-------------|
| 草稿箱 API | ✅ 支持 | ❌ 不支持 |
| 素材上传 API | ✅ 支持 | ❌ 不支持 |
| 本地预览 | ✅ 支持 | ✅ 支持 |
| GUI 复制 | ✅ 支持 | ✅ 支持 |

**未认证订阅号替代方案：**
使用 `preview-gui` 命令生成 GUI 窗口，一键复制内容到公众号编辑器。

---

## 依赖

- Python >= 3.8
- markdown >= 3.4.0
- beautifulsoup4 >= 4.11.0
- pygments >= 2.13.0
- requests >= 2.28.0
- click >= 8.0.0
- pyyaml >= 6.0
- pywebview >= 4.0
- pyperclip >= 1.8
- Pillow >= 9.0

---

## 版本历史

### v1.1.0 (2026-02-25)
- 批量转换功能
- 图片自动压缩
- API 错误重试
- 日志系统
- 本地主题支持

### v1.0.0 (2026-02-21)
- GUI 预览复制
- 图片 Base64 转换
- 自定义主题管理
- 4 种内置主题

### v0.1.0 (2026-02-15)
- 初始版本
- 基础转换
- 图片上传
- 草稿发布

---

## 许可证

MIT License

---

**注意**：使用本工具需要微信公众号的 AppID 和 AppSecret，请妥善保管，不要泄露给他人。
