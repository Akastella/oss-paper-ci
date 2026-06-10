# oss-paper-ci

[English](README.md) | **简体中文** | [日本語](README.ja.md)

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

科研仓库复现准备度检查、复现尝试和复现胶囊打包的命令行工具集。

## 功能

- **scan** — 检查仓库的复现准备度（环境文件、脚本、数据文档、CI 配置）
- **reproduce** — 克隆仓库、安装依赖、运行命令（默认安全模式：dry-run）
- **capsule** — 将复现尝试打包为可验证的证据包
- **batch** — 批量扫描多个项目
- **guide** — 根据角色和主题提供引导式帮助

## 安装

```bash
# 从源码安装（推荐用于开发）
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# 验证安装
oss-paper-ci version
```

## 三个常用命令

```bash
# 1. 扫描仓库
oss-paper-ci scan examples/demo-paper-repo --format markdown

# 2. 尝试复现（安全模式：默认不执行代码）
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# 3. 验证复现胶囊
oss-paper-ci capsule verify repro-capsule.zip
```

## 快速开始

```bash
# 扫描你的仓库
oss-paper-ci scan /path/to/your/repo

# 生成 HTML 报告
oss-paper-ci scan . --format html --output report.html

# 在 GitHub Actions 中使用
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

## 一键复现尝试

```bash
# 安全模式：查看会发生什么（不执行代码）
oss-paper-ci reproduce https://github.com/owner/paper-repo --dry-run

# 执行模式：克隆、安装、运行、生成报告
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --format html --output repro-report.html

# 生成可验证的复现胶囊
oss-paper-ci reproduce examples/demo-reproduce-repo \
  --execute --install --capsule repro-capsule.zip
```

reproduce 命令会克隆仓库、检测环境文件、安装依赖（在隔离的虚拟环境中）、
运行复现命令，并生成结构化报告。默认模式是 dry-run — 需要 `--execute`
才能实际运行代码。

**重要：** 这是*复现尝试*，不是保证复现成功。工具记录的是做了什么，
而不是结果是否正确。

## 复现胶囊

```bash
# 验证胶囊完整性
oss-paper-ci capsule verify repro-capsule.zip

# 查看胶囊内容
oss-paper-ci capsule inspect repro-capsule.zip

# 比较两个胶囊
oss-paper-ci capsule diff old.zip new.zip
```

复现胶囊是包含清单、报告、日志、元数据和 SHA256 完整性校验的
自包含证据包。它**不是**论文正确性的证明。

## 引导模式

```bash
# 获取引导帮助
oss-paper-ci guide
oss-paper-ci guide --role author
oss-paper-ci guide --role reviewer
oss-paper-ci guide --topic reproduce
```

## GitHub Actions

```yaml
- uses: actions/checkout@v4
- uses: Akastella/oss-paper-ci@v1
  with:
    path: "."
    format: "markdown"
```

## 文档

| 主题 | 链接 |
|------|------|
| 入门指南 | [docs/getting-started.md](docs/getting-started.md) |
| 安装 | [docs/installation.md](docs/installation.md) |
| CLI 参考 | [docs/cli-reference.md](docs/cli-reference.md) |
| 安全模型 | [docs/security-model.md](docs/security-model.md) |
| 失败分类 | [docs/failure-taxonomy.md](docs/failure-taxonomy.md) |
| 术语表 | [docs/glossary.md](docs/glossary.md) |
| 角色指南 | [docs/roles.md](docs/roles.md) |
| 复现 | [docs/reproduce.md](docs/reproduce.md) |
| 复现胶囊 | [docs/reproduction-capsules.md](docs/reproduction-capsules.md) |
| 限制 | [docs/limitations.md](docs/limitations.md) |
| 完整索引 | [docs/index.md](docs/index.md) |

## 安全模型

- 默认模式是 **dry-run**：不执行代码，不安装依赖
- `--execute` 才会运行复现命令
- `--install` 才会安装依赖（在隔离的虚拟环境中）
- 危险命令会被阻止（rm -rf、sudo、fork bomb 等）
- 每个命令都有可配置的超时时间

## 限制

- 检查的是复现*准备度*，不是科学正确性
- 不判断论文质量、创新性或录用概率
- 不运行实验（除非明确使用 `--execute`）
- 不解决缺失数据或修复损坏代码
- Python 以外的跨语言检查较浅层
- 分数是工程完整性的指标，不是科学判断

## 失败也是信息

复现尝试失败时，失败报告本身就是有价值的复现证据。
它记录了尝试了什么、在哪里失败、环境是什么样的。
失败不意味着论文有问题 — 可能是环境或依赖问题。

详见 [docs/failure-taxonomy.md](docs/failure-taxonomy.md)。

## 开发

```bash
pip install -e ".[dev]"
python -m pytest
python -m build
python -m twine check dist/*
python scripts/check_docs_truthfulness.py --check
```

## 许可证

MIT — 见 [LICENSE](LICENSE)。
