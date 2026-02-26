# WeChat MP Publisher 基础使用指南

本指南介绍 WeChat MP Publisher 的常用功能和命令，帮助你快速上手。

---

## 目录

1. [安装与配置](#安装与配置)
2. [基础转换](#基础转换)
3. [批量处理](#批量处理)
4. [主题使用](#主题使用)
5. [GUI 预览](#gui-预览)
6. [草稿管理](#草稿管理)
7. [常见问题](#常见问题)

---

## 安装与配置

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourname/wechat-mp-publisher.git
cd wechat-mp-publisher

# 安装依赖
pip install -r requirements.txt

# 安装命令行工具
pip install -e .

# 验证安装
wechat-publisher --version
```

### 配置

#### 方式 1：交互式配置（推荐）

```bash
wechat-publisher config init
```

输入信息：
- **AppID**：微信公众号开发者 ID
- **AppSecret**：微信公众号开发者密码
- **默认作者**：文章默认作者名称

#### 方式 2：环境变量

```bash
export WECHAT_APPID=wx1234567890abcdef
export WECHAT_APPSECRET=your_app_secret_here
```

#### 方式 3：手动设置

```bash
wechat-publisher config set default.author "张三"
wechat-publisher config set default.theme "tech"
```

---

## 基础转换

### 1. 转换并预览

```bash
# 基础转换（生成同名 HTML 文件）
wechat-publisher convert article.md --preview

# 指定输出文件
wechat-publisher convert article.md -o output.html

# 指定主题
wechat-publisher convert article.md --preview --theme tech
```

### 2. 发布到微信草稿箱

```bash
# 基础发布（需要认证服务号）
wechat-publisher convert article.md --draft

# 指定标题和作者
wechat-publisher convert article.md --draft \
  --title "我的文章标题" \
  --author "张三"

# 添加封面（封面需提前上传到微信素材库获取 media_id）
wechat-publisher convert article.md --draft --cover cover.jpg

# 开启评论
wechat-publisher convert article.md --draft --comment

# 仅粉丝可评论
wechat-publisher convert article.md --draft --comment --fans-comment

# 添加原文链接
wechat-publisher convert article.md --draft \
  --source-url "https://example.com/original-post"

# 添加摘要
wechat-publisher convert article.md --draft \
  --digest "这是一篇关于...的文章"
```

### 3. 完整示例

假设有文章 `hello.md`：

```markdown
# 你好，微信公众号

这是我的第一篇文章，使用 WeChat MP Publisher 发布。

## 功能介绍

- **Markdown 转换**：支持标准语法
- **图片上传**：自动上传到微信素材库
- **多主题**：内置 4 种主题

## 代码示例

```python
print("Hello, WeChat!")
```
```

发布命令：

```bash
wechat-publisher convert hello.md --draft \
  --title "你好，微信公众号" \
  --author "张三" \
  --theme tech \
  --comment
```

成功输出：

```
📖 正在读取文件: hello.md
[DRAFT] 使用标题: 你好，微信公众号
THEME: 正在转换（主题: tech）...
[IMAGE]  正在处理图片...
   ✓ 成功上传 0 张图片
🚀 正在发布到微信草稿箱...
[OK] 草稿发布成功！
   Media ID: MEDIA_ID_HERE
   请在微信公众号后台查看草稿
[SUCCESS] 完成！
```

---

## 批量处理

### 场景 1：多文件转换

```bash
# 转换多个文件
wechat-publisher convert article1.md article2.md article3.md --preview

# 生成文件：article1.html, article2.html, article3.html
```

### 场景 2：目录批量转换

```bash
# 转换整个目录
wechat-publisher convert articles/ --preview --output-dir output/

# 递归查找所有 .md 文件
# 生成的 HTML 保存到 output/ 目录
```

### 场景 3：批量发布

```bash
# 批量发布到草稿箱
wechat-publisher convert articles/*.md --draft

# 或使用递归
wechat-publisher convert my-blog/ --draft
```

### 批量转换统计

批量转换完成后会显示统计信息：

```
============================================================
[SUMMARY] 批量转换完成
  成功: 5/5
  失败: 0/5
============================================================
```

---

## 服务器环境使用（OpenClaw/飞书）

在服务器环境（无图形界面）中，无法使用 GUI 预览功能。可以使用以下替代方案：

### 方式 1：生成可复制的内容（推荐）

```bash
# 生成带 Base64 图片的独立 HTML 文件
wechat-publisher copy article.md

# 使用特定主题
wechat-publisher copy article.md --theme tech

# 指定输出文件
wechat-publisher copy article.md -o output.html
```

输出示例：

```
[INFO] 正在处理: article.md
[THEME] 使用主题: default
[BASE64] 正在处理图片...
   ✓ 图片已嵌入 HTML
[OK] HTML 文件已保存: article_copy.html
   文件大小: 245.6 KB

============================================================
使用建议:
  1. 在飞书: 可以直接发送 HTML 文件
  2. 在公众号: 用浏览器打开 HTML 文件，全选复制
  3. 其他平台: 使用生成的 HTML 文件内容
============================================================
```

**特点：**
- 图片已转为 Base64 嵌入 HTML，无需外部文件
- 单个文件即可完整展示
- 可直接在浏览器打开，全选复制到公众号编辑器
- 适合飞书、钉钉等平台分享

### 方式 2：启动 HTTP 服务器

```bash
# 启动临时 HTTP 服务器（默认端口 8080）
wechat-publisher serve article.md

# 指定端口
wechat-publisher serve article.md --port 8888

# 使用特定主题
wechat-publisher serve article.md --theme tech --port 8888
```

输出示例：

```
============================================================
[OK] HTTP 服务器已启动!
============================================================

本地访问: http://localhost:8080
网络访问: http://192.168.1.100:8080

提示:
  - 在飞书或其他平台中可以直接访问上述链接
  - 按 Ctrl+C 停止服务器
============================================================
```

**使用场景：**
- 需要在飞书/钉钉等平台分享预览链接
- 团队成员需要在线查看
- 需要临时展示给其他人

**注意事项：**
- 服务器需要开放相应端口
- 链接仅在服务器运行期间有效
- 按 Ctrl+C 停止服务器

### 方式 3：生成独立 HTML 文件

```bash
# 生成带 Base64 图片的独立 HTML
wechat-publisher convert article.md --base64 --preview

# 指定输出文件
wechat-publisher convert article.md --base64 -o article.html
```

与 `copy` 命令的区别：
- `convert --base64`：仅生成文件，不尝试复制到剪贴板
- `copy`：生成文件并尝试复制到剪贴板（如果环境支持）

---

## 主题使用

### 列出所有主题

```bash
wechat-publisher theme list
```

输出示例：

```
THEME: 可用主题列表:

[BUILTIN] 内置主题:
  - default      - 默认主题，简洁大方，适合大多数文章
  - tech         - 技术主题，代码高亮优化，适合技术文章
  - minimal      - 极简主题，专注内容，无多余装饰
  - elegant      - 优雅主题，衬线字体，适合文学类文章

[CUSTOM]  自定义主题:
  - my-red-theme - 我的红色主题 by Your Name v1.0.0

[TIP] 使用 'theme create <name>' 创建新主题
[TIP] 使用 'theme preview <name> --gui' 预览主题效果
```

### 使用内置主题

```bash
# 默认主题
wechat-publisher convert article.md --preview --theme default

# 技术主题（适合代码文章）
wechat-publisher convert article.md --preview --theme tech

# 极简主题
wechat-publisher convert article.md --preview --theme minimal

# 优雅主题（适合文学类）
wechat-publisher convert article.md --preview --theme elegant
```

### 创建自定义主题

```bash
# 交互式创建
wechat-publisher theme create mytheme

# 创建并保存到当前目录
wechat-publisher theme create mytheme --local

# 创建并保存到指定目录
wechat-publisher theme create mytheme --dir ./themes
```

创建过程示例：

```
THEME: 创建新主题: mytheme

主题描述: 我的自定义主题
作者名称: Your Name

颜色配置（支持 #RRGGBB 格式）:
主色调 [#07c160]: #e74c3c
正文颜色 [#333333]: 
标题颜色 [#000000]: 
背景颜色 [#ffffff]: 
链接颜色 [#e74c3c]: 

字体配置:
字体大小 [16px]: 
行高 [1.8]: 

[OK] 主题已创建: ~/.wechat-mp-publisher/themes/mytheme.css

[TIP] 使用以下命令预览主题:
  wechat-publisher theme preview mytheme
```

### 编辑主题

```bash
# 编辑主题配置
wechat-publisher theme edit mytheme

# 或直接编辑 CSS 文件
vim ~/.wechat-mp-publisher/themes/mytheme.css
```

### 使用本地主题

```bash
# 使用本地主题（相对于当前目录）
wechat-publisher convert article.md --theme .themes/mytheme.css

# 使用绝对路径
wechat-publisher convert article.md --theme /path/to/mytheme.css
```

---

## GUI 预览

GUI 预览功能适用于所有公众号类型，包括未认证订阅号。

### 基础用法

```bash
# 打开 GUI 预览窗口
wechat-publisher preview-gui article.md

# 使用特定主题
wechat-publisher preview-gui article.md --theme tech

# 使用自定义主题
wechat-publisher preview-gui article.md --theme .themes/mytheme.css
```

### 高级选项

```bash
# 不转换图片为 Base64（如果图片太多或太大）
wechat-publisher preview-gui article.md --no-convert-images

# 组合使用
wechat-publisher preview-gui article.md \
  --theme tech \
  --no-convert-images
```

### GUI 使用流程

1. **执行命令** 打开 GUI 窗口
2. **预览效果** 在窗口中查看渲染后的文章
3. **点击复制** 点击"复制全部内容"按钮
4. **粘贴到公众号** 在公众号编辑器中按 Ctrl+V 粘贴

**注意：**
- 图片会自动转为 Base64 格式，确保复制后正常显示
- 推荐使用 Chrome 或 Edge 浏览器内核
- 如果图片太多，可以使用 `--no-convert-images` 选项

---

## 草稿管理

### 列出草稿

```bash
wechat-publisher draft list
```

输出示例：

```
Media ID                      标题                                      更新时间
----------------------------------------------------------------------------------------------------
MEDIA_ID_1                    文章标题 1                                2026-02-25 10:30:00
MEDIA_ID_2                    文章标题 2                                2026-02-24 15:45:00
```

### 查看草稿详情

```bash
wechat-publisher draft get MEDIA_ID_1
```

输出示例：

```
[FILE] 草稿详情
Media ID: MEDIA_ID_1
标题: 文章标题
作者: 张三
摘要: 文章摘要...
原文链接: https://example.com
```

### 删除草稿

```bash
# 交互式确认删除
wechat-publisher draft delete MEDIA_ID_1

# 确认提示：确定要删除这个草稿吗？ [y/N]: 
```

---

## 日志管理

### 查看日志

```bash
# 查看最近 50 行日志
wechat-publisher config logs

# 查看最近 100 行
wechat-publisher config logs -n 100

# 只看错误日志
wechat-publisher config logs --level ERROR

# 只看信息日志
wechat-publisher config logs --level INFO
```

### 清空日志

```bash
wechat-publisher config clear-logs
```

确认提示：确定要清空所有日志文件吗？ [y/N]:

### 日志文件位置

日志文件保存在：`~/.wechat-mp-publisher/logs/`

- `app.log` - 主日志文件（所有级别）
- `error.log` - 错误日志（仅 ERROR 级别）

---

## 调试模式

### 启用详细日志

```bash
# 详细模式（-v）
wechat-publisher -v convert article.md --preview

# 调试模式（--debug）
wechat-publisher --debug convert article.md --preview
```

### 调试信息包括

- 配置文件加载情况
- Token 获取和缓存状态
- API 请求详情
- 图片处理过程
- 转换过程详情

---

## 常见问题

### Q1: 未认证的订阅号可以使用吗？

**可以，但有以下限制：**

| 功能 | 认证服务号 | 未认证订阅号 |
|------|-----------|-------------|
| 草稿箱 API | 支持 | 不支持 |
| GUI 预览复制 | 支持 | 支持 |

**建议未认证订阅号使用 GUI 方式：**

```bash
wechat-publisher preview-gui article.md --theme tech
```

### Q2: 图片上传失败怎么办？

**检查清单：**
1. 图片格式是否为 JPG/PNG/GIF/BMP
2. 图片大小是否超过 2MB（超过会自动压缩）
3. Access Token 是否有效

**查看错误日志：**
```bash
wechat-publisher config logs --level ERROR
```

### Q3: 如何获取 AppID 和 AppSecret？

1. 登录 [微信公众号后台](https://mp.weixin.qq.com)
2. 开发 → 基本配置
3. 查看「开发者ID」
4. 点击「重置」获取 AppSecret

### Q4: 批量转换时如何设置不同标题？

批量转换时，标题会自动从每篇文章的第一个 H1 标题提取。如需自定义标题，建议单独转换每篇文章。

### Q5: 如何更新到最新版本？

```bash
cd wechat-mp-publisher
git pull
pip install -r requirements.txt
pip install -e .
```

---

## 更多资源

- [项目主页](https://github.com/yourname/wechat-mp-publisher)
- [示例文章](./sample-article.md)
- [README.md](../README.md)

---

**祝你使用愉快！**
