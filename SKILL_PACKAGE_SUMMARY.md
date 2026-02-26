# WeChat MP Publisher - OpenClaw Skill 打包摘要

## 基本信息

- **Skill 名称**: wechat-mp-publisher
- **版本**: 1.1.0
- **状态**: 可发布
- **测试状态**: 30个测试全部通过

## 包含文件

### 核心文件（必需）
| 文件 | 说明 |
|------|------|
| `SKILL.md` | OpenClaw Skill 描述文件 |
| `AGENTS.md` | AI Agent 使用指南 |
| `README.md` | 用户完整文档 |
| `LICENSE` | MIT 许可证 |
| `setup.py` | setuptools 打包配置 |
| `pyproject.toml` | 现代 Python 打包配置 |
| `MANIFEST.in` | 包含文件清单 |
| `requirements.txt` | 依赖列表 |

### 源代码
```
src/
├── __init__.py         # 版本信息
├── cli.py              # CLI 入口（所有命令）
├── converter.py        # Markdown → HTML 转换器
├── config.py           # 配置管理
├── logger.py           # 日志系统
├── theme_manager.py    # 主题管理器
├── uploader.py         # 图片上传处理
├── wechat_api.py       # 微信公众号 API 封装
├── image_utils.py      # 图片处理（压缩、Base64）
└── preview_gui.py      # GUI 预览窗口
```

### 主题
```
themes/
├── default.css         # 默认主题
├── tech.css            # 技术主题
├── minimal.css         # 极简主题
└── elegant.css         # 优雅主题
```

### 测试
```
tests/
├── __init__.py
├── test_config.py      # 配置测试（5个）
├── test_converter.py   # 转换器测试（17个）
├── test_uploader.py    # 上传器测试（8个）
└── fixtures/
    └── sample.md       # 测试数据
```

### 示例
```
examples/
├── basic-usage.md      # 基础使用指南
└── sample-article.md   # 示例文章
```

## 功能特性

### v1.1.0 新增功能
- ✅ 批量转换（多文件/目录）
- ✅ 图片自动压缩（>500KB）
- ✅ API 错误重试（指数退避）
- ✅ 完整日志系统
- ✅ 本地主题支持

### 原有功能
- ✅ Markdown → HTML 转换
- ✅ 图片自动上传到微信素材库
- ✅ 4种内置主题 + 自定义主题
- ✅ GUI 预览 + 一键复制
- ✅ 草稿管理（列表/查看/删除）
- ✅ Token 自动管理

## 安装方式

### OpenClaw 安装

```bash
# 方式 1：Git 仓库（推荐）
/skill add https://github.com/yourname/wechat-mp-publisher

# 方式 2：本地路径（开发测试）
/skill add /path/to/wechat-mp-publisher
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/yourname/wechat-mp-publisher.git
cd wechat-mp-publisher

# 安装依赖
pip install -r requirements.txt

# 安装 Skill
pip install -e .
```

## 配置

### 必需配置

```bash
# 交互式配置
wechat-publisher config init

# 输入：
# - AppID（微信公众号开发者 ID）
# - AppSecret（微信公众号开发者密码）
# - 默认作者名称
```

### 环境变量（可选）

```bash
export WECHAT_APPID=wx1234567890abcdef
export WECHAT_APPSECRET=your_secret_here
```

## 常用命令

```bash
# 基础转换
wechat-publisher convert article.md --preview
wechat-publisher convert article.md --draft

# 使用主题
wechat-publisher convert article.md --theme tech --preview

# 批量转换
wechat-publisher convert articles/*.md --preview
wechat-publisher convert articles/ --output-dir output/

# GUI 预览（适合未认证订阅号）
wechat-publisher preview-gui article.md --theme tech

# 主题管理
wechat-publisher theme list
wechat-publisher theme create mytheme
wechat-publisher theme preview mytheme --gui

# 草稿管理
wechat-publisher draft list
wechat-publisher draft get <media_id>
wechat-publisher draft delete <media_id>

# 日志管理
wechat-publisher config logs
wechat-publisher config logs --level ERROR
```

## 使用限制

| 功能 | 认证服务号 | 未认证订阅号 |
|------|-----------|-------------|
| 草稿箱 API | ✅ 支持 | ❌ 不支持 |
| 素材上传 API | ✅ 支持 | ❌ 不支持 |
| 本地预览 | ✅ 支持 | ✅ 支持 |
| GUI 复制 | ✅ 支持 | ✅ 支持 |

**未认证订阅号建议**：使用 `preview-gui` 命令

## 依赖要求

- Python >= 3.8
- markdown >= 3.4.0
- beautifulsoup4 >= 4.11.0
- pygments >= 2.13.0
- requests >= 2.28.0
- click >= 8.0.0
- pyyaml >= 6.0
- pillow >= 9.0.0
- pywebview >= 4.0
- pyperclip >= 1.8

## 验证结果

```
============================================================
WeChat MP Publisher Skill Verification
============================================================

[Required Files]
[OK] OpenClaw Skill description: SKILL.md
[OK] User documentation: README.md
[OK] License file: LICENSE
[OK] setuptools config: setup.py
[OK] Modern packaging config: pyproject.toml
[OK] Package manifest: MANIFEST.in
[OK] Dependencies: requirements.txt

[Source Code]
[OK] Source directory: src
[OK] Themes directory: themes
[OK] Tests directory: tests

[Core Modules]
[OK] All 10 modules present

[Built-in Themes]
[OK] All 4 themes present

[Test Files]
[OK] All test files present

[Version Check]
[OK] Source version: 1.1.0
[OK] pyproject.toml version: 1.1.0

============================================================
[SUCCESS] Skill verification passed!
```

## 测试状态

```bash
$ pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.0.2, pluggy-0.0.0
collected 30 items

tests/test_config.py .....                                              [ 16%]
tests/test_converter.py .................                               [ 73%]
tests/test_uploader.py ........                                         [100%]

============================== 30 passed in 1.5s ==============================
```

## 文档清单

- [x] `SKILL.md` - OpenClaw 标准 Skill 描述
- [x] `AGENTS.md` - Agent 快速参考
- [x] `README.md` - 完整用户文档
- [x] `PACKAGING.md` - 打包指南
- [x] `examples/basic-usage.md` - 基础使用教程
- [x] `examples/sample-article.md` - 示例文章

## 发布检查清单

- [x] 版本号一致（1.1.0）
- [x] 所有测试通过（30/30）
- [x] SKILL.md 符合 OpenClaw 格式
- [x] AGENTS.md 已包含
- [x] LICENSE 文件（MIT）
- [x] 主题文件包含
- [x] 入口点配置正确
- [x] 依赖列表完整
- [x] 文档全面更新

## 打包命令

```bash
# 清理旧构建
rm -rf build/ dist/ *.egg-info

# 构建 wheel
python -m build

# 验证
python verify_skill.py
pytest tests/

# 本地测试安装
pip install dist/wechat_mp_publisher-1.1.0-py3-none-any.whl
```

---

**Skill 已准备就绪，可以发布到 OpenClaw！**
