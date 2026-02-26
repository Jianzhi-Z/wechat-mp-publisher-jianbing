# 服务器环境使用指南

本文档专门针对 OpenClaw、飞书等服务器环境（无图形界面）的使用场景。

## 问题背景

在服务器环境中：
- ❌ 无法打开 GUI 预览窗口（`preview-gui` 命令不可用）
- ❌ 无法直接打开浏览器查看 HTML 文件
- ❌ 无法使用剪贴板（取决于服务器配置）

## 解决方案

### 方案 1：生成可复制的内容（推荐）

使用 `copy` 命令生成完全独立的 HTML 文件：

```bash
wechat-publisher copy article.md
```

**工作流程：**

1. **执行命令**
   ```bash
   wechat-publisher copy article.md --theme tech
   ```

2. **获取输出**
   ```
   [INFO] 正在处理: article.md
   [THEME] 使用主题: tech
   [BASE64] 正在处理图片...
      ✓ 图片已嵌入 HTML
   [OK] HTML 文件已保存: article_copy.html
      文件大小: 245.6 KB
   ```

3. **使用文件**
   - 下载 `article_copy.html` 文件
   - 用浏览器打开
   - 全选 (Ctrl+A) → 复制 (Ctrl+C)
   - 粘贴到公众号编辑器 (Ctrl+V)

**特点：**
- ✅ 图片已转为 Base64 嵌入，无需外部文件
- ✅ 单个文件即可完整展示
- ✅ 可用任何浏览器打开
- ✅ 适合飞书、钉钉等平台分享

**高级选项：**

```bash
# 使用特定主题
wechat-publisher copy article.md --theme tech

# 指定输出文件名
wechat-publisher copy article.md -o my-article.html

# 不尝试复制到剪贴板（纯生成文件）
wechat-publisher copy article.md --no-clipboard
```

---

### 方案 2：启动 HTTP 服务器

使用 `serve` 命令启动临时 HTTP 服务器：

```bash
wechat-publisher serve article.md
```

**工作流程：**

1. **执行命令**
   ```bash
   wechat-publisher serve article.md --port 8080 --theme tech
   ```

2. **获取链接**
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

3. **分享链接**
   - 将 `http://192.168.1.100:8080` 发送到飞书
   - 他人可直接点击链接查看
   - 在浏览器中打开后复制到公众号

**特点：**
- ✅ 提供可访问的 URL 链接
- ✅ 适合团队协作和分享
- ✅ 实时预览，修改 Markdown 后刷新即可

**高级选项：**

```bash
# 指定端口（默认 8080）
wechat-publisher serve article.md --port 8888

# 使用特定主题
wechat-publisher serve article.md --theme elegant

# 自动尝试打开浏览器（服务器环境通常无效）
wechat-publisher serve article.md --open
```

**注意事项：**
- 服务器需要开放相应端口
- 链接仅在服务器运行期间有效
- 按 `Ctrl+C` 停止服务器

---

### 方案 3：生成独立 HTML 文件

使用 `convert` 命令的 `--base64` 选项：

```bash
wechat-publisher convert article.md --base64 --preview
```

**工作流程：**

1. **执行命令**
   ```bash
   wechat-publisher convert article.md --base64 -o output.html
   ```

2. **获取文件**
   - 生成 `output.html` 文件
   - 图片已转为 Base64 嵌入

3. **使用文件**
   - 下载 HTML 文件
   - 浏览器打开后复制到公众号

**与 `copy` 命令的区别：**

| 特性 | `copy` | `convert --base64` |
|------|--------|-------------------|
| 生成独立 HTML | ✅ | ✅ |
| 尝试复制到剪贴板 | ✅ | ❌ |
| 输出提示信息 | 详细 | 简洁 |
| 推荐使用场景 | 交互式使用 | 脚本自动化 |

---

## 飞书平台具体使用流程

### 场景 1：个人使用

```bash
# 1. 生成独立 HTML
wechat-publisher copy article.md --theme tech

# 2. 下载生成的 HTML 文件

# 3. 用浏览器打开，全选复制

# 4. 粘贴到公众号编辑器
```

### 场景 2：团队协作

```bash
# 1. 启动 HTTP 服务器
wechat-publisher serve article.md --port 8080

# 2. 将网络访问链接发送到飞书群
#    "预览链接: http://服务器IP:8080"

# 3. 团队成员点击链接查看

# 4. 确认无误后，复制到公众号
```

### 场景 3：批量处理

```bash
# 1. 批量生成独立 HTML
wechat-publisher convert articles/*.md --base64 --output-dir output/

# 2. 下载 output/ 目录下的所有 HTML 文件

# 3. 分别复制到公众号
```

---

## 常见问题

### Q: `copy` 命令提示无法复制到剪贴板？

这是正常的，服务器环境通常没有剪贴板。HTML 文件已经生成，请手动下载使用。

### Q: `serve` 命令提示端口被占用？

工具会自动尝试其他端口（8080-8090）。也可以手动指定：
```bash
wechat-publisher serve article.md --port 8888
```

### Q: HTTP 服务器链接无法访问？

检查：
1. 服务器防火墙是否开放端口
2. 是否为公网 IP 或内网可访问 IP
3. 飞书/浏览器网络是否正常

### Q: 生成的 HTML 文件太大？

Base64 图片会增加约 33% 的体积。可以：
1. 压缩原图片后再转换
2. 使用 `--no-convert-images` 选项（部分功能）
3. 减少文章中的图片数量

### Q: 如何退出 HTTP 服务器？

按 `Ctrl+C` 停止服务器。

---

## 命令对比

| 命令 | 输出 | 适用场景 | 服务器支持 |
|------|------|----------|-----------|
| `preview-gui` | GUI 窗口 | 本地使用 | ❌ |
| `copy` | HTML 文件 | 生成可复制内容 | ✅ |
| `serve` | HTTP 服务 | 分享预览链接 | ✅ |
| `convert --base64` | HTML 文件 | 脚本自动化 | ✅ |
| `convert --preview` | HTML 文件 | 外部图片引用 | ✅ |

**推荐：**
- **个人使用**：`copy` 命令
- **团队协作**：`serve` 命令
- **批量处理**：`convert --base64`

---

## 快速参考

```bash
# 最常用：生成可复制内容
wechat-publisher copy article.md --theme tech

# 分享链接：启动 HTTP 服务器
wechat-publisher serve article.md --port 8080

# 批量生成
wechat-publisher convert articles/*.md --base64 --output-dir output/
```
