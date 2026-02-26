# WeChat MP Publisher 功能演示

这是一篇示例文章，展示了 WeChat MP Publisher 支持的各种 Markdown 语法和功能特性。

---

## 基础文本样式

### 段落和强调

这是普通段落文本。你可以使用 **粗体** 来强调重要内容，使用 *斜体* 表示术语或外来语，使用 ~~删除线~~ 表示已废弃的内容。

也可以组合使用：***粗斜体***，**~~粗体删除线~~**，*~~斜体删除线~~*。

### 引用块

> 这是一段引用文本。
> 
> 引用块可以包含多行内容，适合用于：
> - 引用他人的话语
> - 强调重要提示
> - 展示引用的代码或配置

> 多级引用也可以：
>> 这是嵌套的引用块
>>> 甚至可以嵌套三层

---

## 列表

### 无序列表

基础用法：

- 第一项
- 第二项
- 第三项

带缩进的层级：

- 前端开发
  - HTML
  - CSS
  - JavaScript
- 后端开发
  - Python
  - Node.js
  - Go
- 数据库
  - MySQL
  - PostgreSQL
  - MongoDB

### 有序列表

步骤说明：

1. 安装 WeChat MP Publisher
2. 配置微信公众号信息
3. 编写 Markdown 文章
4. 执行转换命令
5. 发布到微信公众号

复杂层级：

1. 准备工作
   1. 注册微信公众号
   2. 获取 AppID 和 AppSecret
   3. 安装工具
2. 编写文章
   1. 创建 Markdown 文件
   2. 添加标题和内容
   3. 插入图片和链接
3. 发布流程
   1. 转换 Markdown
   2. 预览效果
   3. 发布到草稿箱

---

## 代码展示

### 行内代码

使用 `pip install wechat-mp-publisher` 安装工具，然后使用 `wechat-publisher --version` 验证安装。

### 代码块

Python 示例：

```python
#!/usr/bin/env python3
"""
WeChat MP Publisher 使用示例
"""

from wechat_mp_publisher import Converter

def publish_article(md_file: str, title: str) -> str:
    """
    发布文章到微信公众号
    
    Args:
        md_file: Markdown 文件路径
        title: 文章标题
        
    Returns:
        草稿 Media ID
    """
    converter = Converter(theme="tech")
    
    # 转换 Markdown
    html_content = converter.convert_file(md_file, title=title)
    
    # 上传到微信
    media_id = upload_to_wechat(html_content)
    
    print(f"文章发布成功！Media ID: {media_id}")
    return media_id

# 使用示例
if __name__ == "__main__":
    result = publish_article("article.md", "我的第一篇文章")
```

JavaScript 示例：

```javascript
// 前端代码示例
const WechatPublisher = {
    config: {
        theme: 'tech',
        autoUpload: true
    },
    
    async convertArticle(mdContent) {
        try {
            const html = await this.parseMarkdown(mdContent);
            const styled = this.applyTheme(html);
            return this.uploadImages(styled);
        } catch (error) {
            console.error('转换失败:', error);
            throw error;
        }
    },
    
    parseMarkdown(content) {
        // Markdown 解析逻辑
        return marked.parse(content);
    }
};

// 使用
WechatPublisher.convertArticle('# 标题\n\n正文内容');
```

Bash 示例：

```bash
#!/bin/bash

# 批量转换脚本
for file in articles/*.md; do
    echo "正在转换: $file"
    wechat-publisher convert "$file" --preview
done

echo "转换完成！"
```

SQL 示例：

```sql
-- 查询示例
SELECT 
    u.username,
    COUNT(a.id) as article_count,
    MAX(a.created_at) as last_published
FROM users u
LEFT JOIN articles a ON u.id = a.user_id
WHERE u.status = 'active'
GROUP BY u.id
ORDER BY article_count DESC
LIMIT 10;
```

---

## 表格

### 功能对比表

| 功能特性 | WeChat MP Publisher | 其他工具 | 备注 |
|---------|---------------------|---------|------|
| 第三方 API 依赖 | 不需要 | 需要 | 直接调用微信 API |
| 完全开源 | 是 | 否 | 代码完全开放 |
| 离线可用 | 是 | 否 | 本地即可完成转换 |
| 自定义样式 | 完全支持 | 有限 | 支持自定义 CSS |
| 批量处理 | 支持 | 不支持 | V1.1 新增 |
| 图片压缩 | 支持 | 不支持 | 自动压缩大图片 |

### 开发进度表

| 模块 | 状态 | 版本 | 说明 |
|------|------|------|------|
| Markdown 转换 | ✅ 完成 | v0.1 | 支持标准语法 |
| 图片上传 | ✅ 完成 | v0.1 | 自动上传到素材库 |
| 主题系统 | ✅ 完成 | v1.0 | 4种内置主题 |
| GUI 预览 | ✅ 完成 | v1.0 | 一键复制功能 |
| 批量转换 | ✅ 完成 | v1.1 | 支持目录批量处理 |
| 错误重试 | ✅ 完成 | v1.1 | 指数退避策略 |
| 日志系统 | ✅ 完成 | v1.1 | 完整日志记录 |

---

## 链接

### 外部链接

- [项目主页](https://github.com/yourname/wechat-mp-publisher)
- [微信公众号开发文档](https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html)
- [Markdown 语法指南](https://www.markdownguide.org/)

### 带标题的链接

[基础使用指南](./basic-usage.md) - 详细的命令使用说明

---

## 图片

### 远程图片

![示例图片](https://via.placeholder.com/600x400/07c160/ffffff?text=WeChat+MP+Publisher)

### 图片说明

WeChat MP Publisher 支持以下图片处理方式：

1. **远程图片** - 自动下载并上传到微信素材库
2. **本地图片** - 自动压缩（如果超过 500KB）并上传
3. **Base64 图片** - 在 GUI 预览时自动转换

---

## 分隔线

上方内容介绍了基础功能。

---

下方内容将介绍高级功能。

---

## 高级功能

### 主题系统

WeChat MP Publisher 内置了 4 种精美主题：

1. **default** - 默认主题
   - 简洁大方的设计
   - 适合大多数类型的文章
   - 配色清爽，阅读舒适

2. **tech** - 技术主题
   - 代码高亮优化
   - 深色代码块背景
   - 适合技术类文章

3. **minimal** - 极简主题
   - 去除多余装饰
   - 专注内容本身
   - 适合长文阅读

4. **elegant** - 优雅主题
   - 使用衬线字体
   - 文艺气息浓厚
   - 适合文学类文章

### 自定义主题

创建自定义主题非常简单：

```bash
# 交互式创建
wechat-publisher theme create mytheme

# 编辑 CSS
vim ~/.wechat-mp-publisher/themes/mytheme.css
```

### 批量转换

支持多种批量转换方式：

- 多个文件：`wechat-publisher convert *.md --preview`
- 整个目录：`wechat-publisher convert articles/ --output-dir output/`
- 递归处理：`wechat-publisher convert my-blog/ --draft`

---

## 使用建议

### 文章结构建议

1. **标题** - 使用 H1 作为主标题（会自动提取）
2. **导语** - 用 1-2 段话概括文章主旨
3. **正文** - 使用 H2/H3 分段，保持段落简短
4. **图片** - 适当插入图片，增强可读性
5. **总结** - 结尾给出要点总结或行动建议

### Markdown 编写技巧

- 使用空行分隔段落，提高可读性
- 代码块标注语言，获得语法高亮
- 使用表格展示对比信息
- 使用引用块强调重要内容
- 适当使用粗体和斜体突出重点

---

## 结语

感谢使用 WeChat MP Publisher！

这个工具旨在让微信公众号写作更加高效、愉悦。通过 Markdown 编写，你可以专注于内容本身，而不必纠结于排版和格式。

如果你有任何建议或遇到问题，欢迎提交 Issue 或 PR。

**Happy Writing!** ✍️

---

*本文档由 WeChat MP Publisher 自动生成*
