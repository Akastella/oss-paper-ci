# OSS-Paper-CI

[English](README.md) | **简体中文** | [日本語](README.ja.md)

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

科研仓库复现证据的命令行工具集：检查、尝试、打包、解释。

```bash
# 不知道从哪开始？
oss-paper-ci wizard

# 运行完整流水线
oss-paper-ci workbench .

# 安全复现尝试（默认不执行代码）
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
```

OSS-Paper-CI 记录和解释复现证据。它不证明科学正确性，不判断论文质量，不预测录用结果。

## 快速开始

```bash
# 1. 从 GitHub 安装
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e .

# 2. 60 秒试用
oss-paper-ci try-demo

# 3. 扫描你的仓库
oss-paper-ci scan .
```

**其他安装方式：** 参见 [安装文档](docs/installation.md) 了解 pipx、wheel 和源码安装选项。

> **注意：** oss-paper-ci 尚未在 PyPI 上发布，请从 GitHub 源码安装。

## 首次运行

```bash
# 获取个性化推荐
oss-paper-ci quickstart

# 主题特定指南
oss-paper-ci quickstart --topic install
oss-paper-ci quickstart --topic github-action
oss-paper-ci quickstart --topic reproduce
oss-paper-ci quickstart --topic eval
```

## 评估

项目包含一个 **synthetic-but-realistic 评估语料库**，用于验证工具在不同科研仓库状态下的输出稳定性。

```bash
# 运行评估
oss-paper-ci eval run examples/evaluation-corpus

# 生成 JSON 报告
oss-paper-ci eval run examples/evaluation-corpus --format json --output report.json

# 与基线对比
oss-paper-ci eval compare --baseline tests/golden/evaluation_summary.json --current report.json
```

评估语料库包含 12+ 个合成仓库，覆盖：
- Python（良好复现、缺少数据、缺少环境、结果异常）
- R、Julia、Node.js、Make、Snakemake、C++ 项目
- 不安全脚本检测
- 采纳前后对比

**重要说明：** 这些是合成测试用例，不是真实世界仓库。基准测试展示的是工具稳定性，而非科学正确性。

## 功能一览

| 功能 | 命令 | 说明 |
|------|------|------|
| 准备度扫描 | `oss-paper-ci scan .` | 检查复现准备度并给出评分和建议 |
| 数据诊断 | `oss-paper-ci data diagnose .` | 检查数据文档和可用性 |
| 结果验证 | `oss-paper-ci results validate .` | 验证声称的结果是否有证据支撑 |
| 安全复现 | `oss-paper-ci reproduce URL --dry-run` | 不执行代码的复现尝试 |
| 复现编排器 | `oss-paper-ci reproduce plan/run/report` | 规划、执行和验证复现工作流 |
| 复现胶囊 | `oss-paper-ci capsule verify out.zip` | 验证和查看证据包 |
| 复现摘要 | `oss-paper-ci dossier .` | 生成面向作者/审稿人/维护者的摘要 |
| 批量扫描 | `oss-paper-ci batch scan --workspace ws.yml` | 从配置文件批量扫描多个项目 |
| 生态检测 | `oss-paper-ci ecosystems detect .` | 检测 Python、R、Julia、MATLAB 等 |
| 终端工作台 | `oss-paper-ci workbench .` | 多步流水线带进度显示 |
| 向导 | `oss-paper-ci wizard` | 为新用户提供安全的下一步建议 |
| 信任审计 | `oss-paper-ci trust audit .` | 本地静态信任和工作流审计 |
| 安全扫描 | `oss-paper-ci security scan .` | 扫描密钥、危险模式、Docker 风险 |
| 依赖清单 | `oss-paper-ci trust inventory .` | 类 SBOM 依赖清单 |
| 来源证明 | `oss-paper-ci trust provenance .` | 生成本地来源证明清单 |
| 产物验证 | `oss-paper-ci trust verify-artifacts .` | 验证 SHA256 校验和 |

## 安全模型

- 默认模式是 **dry-run**：不执行代码，不安装依赖
- `--execute` 才会运行复现命令
- `--install` 才会安装依赖（在隔离的虚拟环境中）
- 危险命令会被阻止（rm -rf、sudo、fork bomb 等）
- 每个命令都有可配置的超时时间
- 详见 [docs/security-model.md](docs/security-model.md)

## 使用示例

```bash
# 扫描仓库
oss-paper-ci scan .

# 完整流水线带输出文件
oss-paper-ci workbench . --output-dir results

# 安全复现尝试
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# CI 集成
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

工作流模板见 [examples/github-actions/](examples/github-actions/)。

## 信任与安全

OSS-Paper-CI 可以做本地静态信任检查，例如工作流权限、疑似密钥、危险脚本模式、依赖清单和发布产物校验。它不是安全认证，也不会证明仓库绝对安全。

```bash
# 信任审计（工作流风险、权限、action 版本）
oss-paper-ci trust audit .

# 安全扫描（密钥、危险模式、Docker 风险）
oss-paper-ci security scan .

# 依赖清单（类 SBOM）
oss-paper-ci trust inventory .

# 来源证明清单
oss-paper-ci trust provenance .

# 验证发布产物
oss-paper-ci trust verify-artifacts release-artifacts/
```

**重要说明：** 这些只是本地静态分析检查，不是安全认证，不验证第三方完整性，也不声称符合 SLSA、Sigstore 或 SPDX 标准。完整威胁模型和限制见 [SECURITY.md](SECURITY.md)。

## 统一证据报告

统一证据报告会把复现准备度、环境、数据、结果、执行入口、信任检查和安全边界整合到一份报告中。它帮助作者和审查者沟通"仓库提供了哪些复现证据"，但不证明论文科学结论正确，也不预测录用结果。

```bash
# 面向审查者的报告
oss-paper-ci evidence . --profile reviewer --format html --output evidence.html

# 面向作者的报告
oss-paper-ci evidence . --profile author --format markdown

# 生成可分享的证据包
oss-paper-ci evidence bundle . --output evidence-bundle.zip

# 验证证据包完整性
oss-paper-ci evidence verify evidence-bundle.zip
```

详见 [docs/evidence-report.md](docs/evidence-report.md)。

## 复现编排器

复现编排器可以读取仓库中的 `reproducibility.yml`，生成执行计划，在显式授权后运行声明的命令，收集日志、产物和指标，并生成复现报告。它不会默认执行代码，也不会证明论文结论正确；它只记录声明流程是否能够被安全、可追踪地执行。

```bash
# 生成计划（不执行代码）
oss-paper-ci reproduce plan examples/repro-system-demo

# 显式授权后执行
oss-paper-ci reproduce run examples/repro-system-demo --execute --sandbox local

# 生成 HTML 报告
oss-paper-ci reproduce report .oss-paper-ci-repro-run --format html --output reproduction.html

# 对比预期值
oss-paper-ci reproduce compare .oss-paper-ci-repro-run --expected examples/repro-system-demo/reproducibility.yml

# 生成证据包
oss-paper-ci reproduce bundle .oss-paper-ci-repro-run --output reproduction-evidence.zip
```

详见 [docs/reproduction-orchestrator.md](docs/reproduction-orchestrator.md)。

## 文档

| 主题 | 链接 |
|------|------|
| 入门指南 | [docs/getting-started.md](docs/getting-started.md) |
| CLI 参考 | [docs/cli-reference.md](docs/cli-reference.md) |
| 终端工作台 | [docs/terminal-workbench.md](docs/terminal-workbench.md) |
| 项目简介 | [docs/project-summary.md](docs/project-summary.md) |
| 示例报告 | [docs/demo-gallery.md](docs/demo-gallery.md) |
| 完整索引 | [docs/index.md](docs/index.md) |

## 限制

- 检查的是复现*准备度*，不是科学正确性
- 不判断论文质量、创新性或录用概率
- 不运行实验（除非明确使用 `--execute`）
- 不解决缺失数据或修复损坏代码
- 分数是工程完整性的指标，不是科学判断

详见 [docs/limitations.md](docs/limitations.md)。

## 开发

```bash
pip install -e ".[dev]"
python -m pytest
python scripts/check_docs_truthfulness.py --check
```

## 许可证

MIT — 见 [LICENSE](LICENSE)。
