# WeChat MP Publisher

<p align="center">
  将 Markdown 一键发布到微信公众号草稿箱
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#使用方法">使用方法</a> •
  <a href="#主题定制">主题定制</a> •
  <a href="#常见问题">常见问题</a>
</p>

---

## 为什么选择 WeChat MP Publisher？

| 特性 | 其他工具 | WeChat MP Publisher |
|------|---------|---------------------|
| 第三方 API 依赖 | 需要 | **不需要** |
| 完全开源 | 否 | **是** |
| 离线可用 | 否 | **是** |
| 直接调用微信 API | 间接 | **直接** |
| 自定义样式 | 有限 | **完全支持** |
| 批量处理 | 不支持 | **支持** |
| 图片自动压缩 | 不支持 | **支持** |

## 功能特性

- **一键发布** - Markdown 转 HTML，自动上传到微信草稿箱
- **多主题样式** - 4 种内置主题，支持完全自定义 CSS
- **图片自动处理** - 本地/远程图片自动上传到微信素材库，自动压缩
- **批量转换** - 支持多个文件或整个目录批量处理
- **错误重试** - API 调用失败自动重试（指数退避策略）
- **日志记录** - 完整的日志系统，便于排查问题
- **Token 自动管理** - 自动获取、缓存和刷新 Access Token
- **完全离线** - 不依赖任何第三方服务

### 开发进度

| 功能模块 | 状态 | 说明 |
|----------|------|------|
| Markdown 转换 | 完成 | 支持标准语法、代码高亮、表格、删除线 |
| 主题系统 | 完成 | 4种内置主题 + 自定义CSS + 本地/全局主题 |
| CLI 命令 | 完成 | convert、config、theme、draft |
| 配置管理 | 完成 | 配置文件 + 环境变量 |
| 批量转换 | 完成 | V1.1 新增，支持多文件和目录 |
| 图片压缩 | 完成 | V1.1 新增，自动压缩 >500KB 图片 |
| 错误重试 | 完成 | V1.1 新增，指数退避重试 |
| 日志系统 | 完成 | V1.1 新增，支持查看和清空 |
| GUI 预览复制 | 完成 | V1.0 已完成，支持一键复制到公众号 |
| 单元测试 | 完成 | 30个测试全部通过 |
| 草稿发布 API | 受限 | 需微信认证服务号 |

**注意：** 如果你的公众号是未认证的订阅号，无法使用草稿箱API功能，可以使用 `--preview` 生成本地 HTML，或使用 `preview-gui` 命令打开 GUI 窗口一键复制到公众号编辑器。

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourname/wechat-mp-publisher.git
cd wechat-mp-publisher

# 安装依赖
pip install -r requirements.txt

# 安装命令行工具
pip install -e .
```

### 配置

```bash
# 初始化配置
wechat-publisher config init

# 根据提示输入：
# - AppID（微信公众号开发者 ID）
# - AppSecret（微信公众号开发者密码）
# - 默认作者名称
```

### 第一个文章

```bash
# 创建 Markdown 文件
cat > article.md << 'EOF'
# 我的第一篇文章

这是我的第一篇微信公众号文章。

## 功能介绍

- Markdown 转换
- 图片自动上传
- 多主题支持
EOF

# 预览效果
wechat-publisher convert article.md --preview

# 发布到微信草稿箱（需要认证服务号）
wechat-publisher convert article.md --draft

# 或使用 GUI 预览并复制（适用于所有公众号）
wechat-publisher preview-gui article.md
```

---

## 使用方法

### 基础命令

```bash
# 转换并预览（生成 HTML 文件）
wechat-publisher convert article.md --preview

# 转换并指定输出文件
wechat-publisher convert article.md -o output.html

# 转换并发布到草稿箱
wechat-publisher convert article.md --draft

# 指定标题和作者
wechat-publisher convert article.md --draft \
  --title "文章标题" \
  --author "作者名"

# 添加封面图片（封面需要提前上传到微信素材库）
wechat-publisher convert article.md --draft --cover cover.jpg

# 开启评论
wechat-publisher convert article.md --draft --comment

# 仅粉丝可评论
wechat-publisher convert article.md --draft --comment --fans-comment
```

### 批量转换

```bash
# 转换多个文件
wechat-publisher convert article1.md article2.md article3.md --preview

# 转换整个目录（自动生成 HTML 文件）
wechat-publisher convert articles/ --preview --output-dir output/

# 批量发布到草稿箱
wechat-publisher convert articles/*.md --draft

# 递归转换目录下的所有 Markdown 文件
wechat-publisher convert my-blog/ --preview --output-dir html/
```

### GUI 预览与复制

```bash
# 打开 GUI 窗口预览（支持一键复制到公众号编辑器）
wechat-publisher preview-gui article.md

# 使用特定主题
wechat-publisher preview-gui article.md --theme tech

# 不转换图片为 Base64（如果图片太多）
wechat-publisher preview-gui article.md --no-convert-images
```

GUI 窗口功能：
- 实时预览转换后的文章效果
- 点击"复制全部内容"按钮，直接粘贴到公众号编辑器
- 图片自动转为 Base64，确保复制后正常显示

### 主题使用

```bash
# 列出所有主题
wechat-publisher theme list

# 使用技术主题（适合代码文章）
wechat-publisher convert article.md --theme tech --draft

# 使用优雅主题（适合文学类）
wechat-publisher convert article.md --theme elegant --draft

# 使用自定义主题（全局主题）
wechat-publisher convert article.md --theme mytheme --draft

# 使用本地主题（指定路径）
wechat-publisher convert article.md --theme .themes/mytheme.css --draft

# 预览主题效果
wechat-publisher theme preview tech --gui
```

### 主题管理

```bash
# 创建新主题（交互式向导）
wechat-publisher theme create mytheme

# 创建主题并保存到当前目录
wechat-publisher theme create mytheme --local

# 创建主题并保存到指定目录
wechat-publisher theme create mytheme --dir ./assets/themes

# 编辑主题配置
wechat-publisher theme edit mytheme

# 导出主题
wechat-publisher theme export mytheme

# 导入外部 CSS 文件
wechat-publisher theme import /path/to/style.css --name imported_theme

# 删除自定义主题
wechat-publisher theme delete mytheme
```

### 草稿管理

```bash
# 列出所有草稿
wechat-publisher draft list

# 查看草稿详情
wechat-publisher draft get <media_id>

# 删除草稿
wechat-publisher draft delete <media_id>
```

### 配置管理

```bash
# 初始化配置
wechat-publisher config init

# 查看配置
wechat-publisher config list

# 设置配置项
wechat-publisher config set default.author "作者名"
wechat-publisher config set default.theme "tech"

# 获取配置项
wechat-publisher config get default.theme

# 查看日志
wechat-publisher config logs

# 查看最近的错误日志
wechat-publisher config logs --level ERROR

# 查看最近 100 行日志
wechat-publisher config logs -n 100

# 清空日志
wechat-publisher config clear-logs
```

### 调试模式

```bash
# 启用详细日志输出
wechat-publisher -v convert article.md --preview

# 启用调试模式（最详细，包括 API 请求详情）
wechat-publisher --debug convert article.md --preview

# 查看完整帮助
wechat-publisher --help
wechat-publisher convert --help
wechat-publisher theme --help
```

---

## 主题定制

### 内置主题

| 主题 | 描述 | 适用场景 |
|------|------|----------|
| `default` | 简洁大方，配色清爽 | 通用文章 |
| `tech` | 代码高亮优化，深色代码块 | 技术文章 |
| `minimal` | 极简风格，去除多余装饰 | 专注阅读 |
| `elegant` | 衬线字体，文艺气息 | 文学类文章 |

### 快速创建自定义主题

```bash
$ wechat-publisher theme create my-red-theme

THEME: 创建新主题: my-red-theme

主题描述: 我的红色主题
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

[OK] 主题已创建: ~/.wechat-mp-publisher/themes/my-red-theme.css
```

### 主题保存位置

**全局主题**（所有项目可用）：
```bash
wechat-publisher theme create mytheme
# 保存到: ~/.wechat-mp-publisher/themes/mytheme.css
```

**本地主题**（当前项目专属）：
```bash
wechat-publisher theme create mytheme --local
# 保存到: ./.themes/mytheme.css
```

**指定目录**：
```bash
wechat-publisher theme create mytheme --dir ./assets/themes
# 保存到: ./assets/themes/mytheme.css
```

### 手动编辑 CSS

主题文件可以直接编辑：

```bash
# 编辑全局主题
vim ~/.wechat-mp-publisher/themes/mytheme.css

# 编辑本地主题
vim .themes/mytheme.css
```

自定义主题 CSS 结构：

```css
/*
 * 主题: mytheme
 * 描述: 我的自定义主题
 */

.mp-article {
    /* 基础样式 */
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    background-color: #fff;
}

/* 标题样式 */
.mp-article h1 {
    font-size: 24px;
    font-weight: bold;
    color: #000;
    margin: 24px 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e74c3c;  /* 使用主色调 */
}

.mp-article h2 {
    font-size: 20px;
    font-weight: bold;
    color: #000;
    margin: 20px 0 12px;
    padding-left: 12px;
    border-left: 4px solid #e74c3c;
}

/* 段落 */
.mp-article p {
    margin: 16px 0;
    text-align: justify;
}

/* 引用块 */
.mp-article blockquote {
    margin: 16px 0;
    padding: 12px 16px;
    background: #f5f5f5;
    border-left: 4px solid #e74c3c;
    color: #666;
}

/* 代码块 */
.mp-article pre {
    background: #f8f8f8;
    padding: 16px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 14px;
}

/* 行内代码 */
.mp-article code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 14px;
}

/* 链接 */
.mp-article a {
    color: #e74c3c;
    text-decoration: none;
}

/* 图片 */
.mp-article img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 16px auto;
}

/* 表格 */
.mp-article table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
}

.mp-article th,
.mp-article td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

.mp-article th {
    background: #f5f5f5;
    font-weight: bold;
}

/* 列表 */
.mp-article ul,
.mp-article ol {
    margin: 16px 0;
    padding-left: 24px;
}

.mp-article li {
    margin: 8px 0;
}

/* 分隔线 */
.mp-article hr {
    border: none;
    border-top: 1px solid #eee;
    margin: 24px 0;
}

/* 删除线 */
.mp-article del {
    text-decoration: line-through;
    color: #999;
}
```

---

## 支持的 Markdown 语法

- **标题** - H1-H6，支持从标题自动提取文章标题
- **粗体** - `**粗体**`
- **斜体** - `*斜体*`
- **删除线** - `~~删除线~~`
- **有序列表** - `1. 项目`
- **无序列表** - `- 项目`
- **链接** - `[链接文字](https://example.com)`
- **图片** - `![图片描述](image.png)`，支持本地和远程图片
- **引用块** - `> 引用内容`
- **代码块** - 支持语法高亮
- **表格** - 标准 Markdown 表格
- **分隔线** - `---`
- **行内代码** - `` `代码` ``

### 代码高亮示例

支持 100+ 种编程语言的高亮：

```python
# Python 示例
def hello_wechat():
    """向微信公众号问好"""
    print("Hello, WeChat MP!")
    return "success"

result = hello_wechat()
```

```javascript
// JavaScript 示例
const greeting = () => {
    console.log("Hello from JavaScript!");
};
```

```bash
# Bash 示例
wechat-publisher convert article.md --draft
```

---

## 项目结构

```
wechat-mp-publisher/
├── src/                          # 源代码
│   ├── __init__.py
│   ├── cli.py                    # CLI 入口（所有命令）
│   ├── config.py                 # 配置管理
│   ├── converter.py              # Markdown → HTML 转换器
│   ├── image_utils.py            # 图片处理（Base64、压缩）
│   ├── logger.py                 # 日志系统
│   ├── preview_gui.py            # GUI 预览窗口
│   ├── theme_manager.py          # 主题管理器
│   ├── uploader.py               # 图片上传处理器
│   └── wechat_api.py             # 微信公众号 API 封装
├── themes/                       # 内置主题
│   ├── default.css
│   ├── tech.css
│   ├── minimal.css
│   └── elegant.css
├── tests/                        # 测试
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_converter.py
│   ├── test_uploader.py
│   └── fixtures/
│       └── sample.md
├── examples/                     # 示例
│   ├── basic-usage.md
│   └── sample-article.md
├── README.md                     # 本文件
├── SKILL.md                      # OpenClaw Skill 描述
├── requirements.txt              # Python 依赖
├── setup.py                      # 安装配置
└── run_tests.py                  # 测试运行脚本
```

---

## 常见问题

### Q: 如何获取微信公众号的 AppID 和 AppSecret？

1. 登录 [微信公众号后台](https://mp.weixin.qq.com)
2. 左侧菜单 → 开发 → 基本配置
3. 查看「开发者ID」部分的 AppID
4. 点击「重置」获取 AppSecret（注意：AppSecret 只显示一次，请妥善保存）

**注意：** 只有管理员才能查看和重置 AppSecret。

### Q: 未认证的订阅号可以使用吗？

可以，但有限制：

| 功能 | 认证服务号 | 未认证订阅号 |
|------|-----------|-------------|
| 草稿箱 API | 支持 | 不支持 |
| 素材上传 API | 支持 | 不支持 |
| 本地预览 | 支持 | 支持 |
| GUI 复制 | 支持 | 支持 |

**替代方案：** 使用 `preview-gui` 命令：
```bash
wechat-publisher preview-gui article.md --theme tech
```
然后在 GUI 窗口中点击"复制全部内容"，直接粘贴到公众号编辑器。

### Q: 图片上传失败怎么办？

检查以下几点：
1. 图片格式是否为 JPG/PNG/GIF/BMP
2. 图片大小是否超过 2MB（超过会自动压缩）
3. Access Token 是否有效（可尝试 `wechat-publisher config init` 重新配置）
4. 查看日志：`wechat-publisher config logs --level ERROR`

### Q: 如何创建自己的主题？

使用交互式创建命令：
```bash
wechat-publisher theme create mytheme
```

或手动创建 CSS 文件：
```bash
mkdir -p ~/.wechat-mp-publisher/themes
cat > ~/.wechat-mp-publisher/themes/mytheme.css << 'EOF'
.mp-article { font-family: "PingFang SC", sans-serif; }
.mp-article h1 { color: #e74c3c; }
EOF
```

### Q: 批量转换时如何指定不同的标题？

批量转换时，标题会自动从每篇文章的第一个 H1 标题提取。如果文章没有 H1，则使用文件名作为标题。

如需自定义标题，建议单独转换每篇文章。

### Q: 如何调试转换结果？

1. **本地预览**：
   ```bash
   wechat-publisher convert article.md --preview -o preview.html
   ```

2. **调试模式**：
   ```bash
   wechat-publisher --debug convert article.md --preview
   ```

3. **查看日志**：
   ```bash
   wechat-publisher config logs -n 50
   ```

### Q: 日志文件在哪里？

日志文件保存在：`~/.wechat-mp-publisher/logs/`
- `app.log` - 主日志文件
- `error.log` - 错误日志（仅包含 ERROR 级别）

### Q: 如何更新到最新版本？

```bash
cd wechat-mp-publisher
git pull
pip install -r requirements.txt
pip install -e .
```

---

## 开发

### 运行测试

```bash
# 使用 pytest
pytest tests/ -v

# 或使用提供的脚本
python run_tests.py
```

### 项目依赖

- Python >= 3.8
- markdown >= 3.4.0 - Markdown 解析
- beautifulsoup4 >= 4.11.0 - HTML 处理
- pygments >= 2.13.0 - 代码高亮
- requests >= 2.28.0 - HTTP 请求
- click >= 8.0.0 - CLI 框架
- pyyaml >= 6.0 - YAML 解析
- pywebview >= 4.0 - GUI 预览
- pyperclip >= 1.8 - 剪贴板操作
- Pillow >= 9.0 - 图片处理

---

## 更新日志

### v1.1.0 (2026-02-25)

- 新增：批量转换功能（支持多文件和目录）
- 新增：图片自动压缩（超过 500KB 自动压缩）
- 新增：API 错误重试机制（指数退避）
- 新增：完整日志系统（支持查看和清空）
- 新增：本地主题支持（项目专属主题）
- 优化：主题创建交互式向导
- 优化：GUI 预览复制功能

### v1.0.0 (2026-02-21)

- 新增：GUI 预览窗口（支持一键复制）
- 新增：图片 Base64 转换
- 新增：自定义主题管理
- 新增：4 种内置主题
- 优化：完整的错误处理

### v0.1.0 (2026-02-15)

- 初始版本发布
- Markdown 基础转换
- 图片自动上传
- 草稿发布功能
- Token 自动管理

---

## 许可证

[MIT License](LICENSE)

---

## 致谢

- [markdown](https://github.com/Python-Markdown/markdown) - Markdown 解析库
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML 处理库
- [Pygments](https://pygments.org/) - 代码高亮库
- [Click](https://click.palletsprojects.com/) - CLI 框架
- [pywebview](https://pywebview.flowrl.com/) - GUI 框架

---

<p align="center">
  Made with ❤️ for WeChat MP Publishers
</p>
