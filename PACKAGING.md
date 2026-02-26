# OpenClaw Skill 打包指南

本文档说明如何将 WeChat MP Publisher 打包为 OpenClaw Skill。

## 目录结构

```
wechat-mp-publisher/
├── SKILL.md              # OpenClaw Skill 描述文件（必需）
├── AGENTS.md             # Agent 使用指南
├── README.md             # 用户文档
├── LICENSE               # MIT 许可证
├── setup.py              # setuptools 配置
├── pyproject.toml        # 现代 Python 打包配置
├── MANIFEST.in           # 包含文件清单
├── requirements.txt      # 依赖列表
├── src/                  # 源代码
├── themes/               # 主题 CSS 文件
├── tests/                # 测试文件
└── examples/             # 示例文件
```

## 打包步骤

### 1. 安装打包工具

```bash
pip install build twine
```

### 2. 构建分发包

```bash
# 清理旧构建
rm -rf build/ dist/ *.egg-info

# 构建 wheel 和 sdist
python -m build
```

### 3. 验证构建

```bash
# 检查生成的文件
ls -lh dist/

# 验证 wheel
python -m twine check dist/*
```

### 4. 本地安装测试

```bash
# 创建虚拟环境
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 安装
pip install dist/wechat_mp_publisher-1.1.0-py3-none-any.whl

# 测试
wechat-publisher --version
wechat-publisher --help
```

### 5. 运行测试

```bash
pytest tests/ -v
```

## OpenClaw 安装

### 方式 1：Git 仓库（推荐）

```bash
# 在 OpenClaw 中添加 Skill
/skill add https://github.com/yourname/wechat-mp-publisher
```

### 方式 2：本地路径

```bash
# 本地开发测试
/skill add /path/to/wechat-mp-publisher
```

### 方式 3：PyPI（如发布）

```bash
pip install wechat-mp-publisher
```

## Skill 配置

安装后需要配置微信公众号信息：

```bash
# 方式 1：交互式配置
wechat-publisher config init

# 方式 2：环境变量
export WECHAT_APPID=wx1234567890abcdef
export WECHAT_APPSECRET=your_secret_here
```

## 文件说明

### SKILL.md

OpenClaw Skill 的描述文件，包含：
- Skill 名称和描述
- 功能特性
- 安装和使用方法
- 依赖要求

### AGENTS.md

面向 AI Agent 的指南，包含：
- 快速理解项目
- 常用命令
- 项目结构
- 开发指南

### setup.py & pyproject.toml

Python 包配置：
- `setup.py`: 传统 setuptools 配置
- `pyproject.toml`: 现代标准配置（PEP 518/621）

### MANIFEST.in

确保以下文件被打包：
- README.md, LICENSE, SKILL.md
- themes/*.css（主题文件）
- examples/*.md（示例文件）
- tests/*.py（测试文件）

## 版本更新

更新版本时需要修改：

1. `src/__init__.py`: `__version__`
2. `setup.py`: `version`
3. `pyproject.toml`: `version`
4. `SKILL.md`: 版本历史
5. `README.md`: 更新日志

## 发布到 PyPI（可选）

```bash
# 1. 构建
python -m build

# 2. 上传测试环境
python -m twine upload --repository testpypi dist/*

# 3. 上传正式环境
python -m twine upload dist/*
```

## 常见问题

### Q: 主题文件没有被打包？

确保 `MANIFEST.in` 包含：
```
recursive-include themes *.css
```

并在 `pyproject.toml` 中：
```toml
[tool.setuptools.package-data]
"*" = ["*.css", "*.html", "*.yaml", "*.json"]
```

### Q: 安装后命令找不到？

检查 `pyproject.toml` 中的入口点：
```toml
[project.scripts]
wechat-publisher = "src.cli:main"
```

### Q: 测试失败？

确保测试依赖已安装：
```bash
pip install -e ".[dev]"
```

## 验证清单

发布前检查：

- [ ] 版本号一致（__init__.py, setup.py, pyproject.toml）
- [ ] 所有测试通过
- [ ] SKILL.md 内容完整
- [ ] AGENTS.md 已更新
- [ ] LICENSE 文件存在
- [ ] 主题文件包含在包中
- [ ] 本地安装测试通过
- [ ] 命令行工具可用
