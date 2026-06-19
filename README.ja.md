# OSS-Paper-CI

[English](README.md) | [简体中文](README.zh-CN.md) | **日本語**

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

科学リポジトリの再現性証拠をチェック、試行、パッケージ化、説明するためのCLIツールキット。

```bash
# 何から始めればいいかわからない場合
oss-paper-ci wizard

# フルパイプラインを実行
oss-paper-ci workbench .

# 安全な再現試行（デフォルトではコードを実行しない）
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
```

OSS-Paper-CI は再現性の証拠を記録し説明します。科学的正しさを証明したり、論文の品質を判断したり、採択を予測したりするものではありません。

## クイックスタート

```bash
# インストール
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# ガイド付き推奨事項を取得
oss-paper-ci wizard

# フルパイプラインを実行
oss-paper-ci workbench .

# リポジトリをスキャン
oss-paper-ci scan .

# 安全な再現試行
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
```

## 評価

このプロジェクトには、異なる研究リポジトリ状態に対する出力の安定性を検証するための **synthetic-but-realistic な評価コーパス** が含まれています。

```bash
# 評価の実行
oss-paper-ci eval run examples/evaluation-corpus

# JSON レポートの生成
oss-paper-ci eval run examples/evaluation-corpus --format json --output report.json

# ベースラインとの比較
oss-paper-ci eval compare --baseline tests/golden/evaluation_summary.json --current report.json
```

評価コーパスには 12+ の合成リポジトリが含まれ、以下をカバーします：
- Python（良好な再現性、データ欠落、環境欠落、結果異常）
- R、Julia、Node.js、Make、Snakemake、C++ プロジェクト
- 安全でないスクリプトの検出
- 採用前後の比較

**重要な注意：** これらは合成テストフィクスチャであり、実世界のリポジトリではありません。ベンチマークはツールの安定性を示すものであり、科学的正しさを証明するものではありません。

## 機能一覧

| 機能 | コマンド | 説明 |
|------|----------|------|
| 準備度スキャン | `oss-paper-ci scan .` | 再現準備度をスコア化し推奨事項を提示 |
| データ診断 | `oss-paper-ci data diagnose .` | データ文書と可用性をチェック |
| 結果検証 | `oss-paper-ci results validate .` | 主張された結果が証拠に裏付けられているか検証 |
| 安全な再現 | `oss-paper-ci reproduce URL --dry-run` | コードを実行しない再現試行 |
| 再現カプセル | `oss-paper-ci capsule verify out.zip` | 証拠パッケージの検証と確認 |
| 再現ドシエ | `oss-paper-ci dossier .` | 著者/レビュアー/メンテナー向けの要約を生成 |
| ワークスペースバッチ | `oss-paper-ci batch scan --workspace ws.yml` | 設定ファイルから複数プロジェクトをスキャン |
| エコシステム検出 | `oss-paper-ci ecosystems detect .` | Python、R、Julia、MATLABなどを検出 |
| ターミナルワークベンチ | `oss-paper-ci workbench .` | 進行状況表示付きマルチステップパイプライン |
| ウィザード | `oss-paper-ci wizard` | 新規ユーザー向けの安全な次のステップを提案 |

## セキュリティモデル

- デフォルトモードは **dry-run**：コードは実行されず、依存関係はインストールされない
- `--execute` で再現コマンドが実行される
- `--install` で依存関係がインストールされる（隔離された仮想環境内）
- 危険なコマンドはブロックされる（rm -rf、sudo、fork bombなど）
- すべてのコマンドに設定可能なタイムアウトがある
- 詳細は [docs/security-model.md](docs/security-model.md)

## 使用例

```bash
# リポジトリをスキャン
oss-paper-ci scan .

# 出力ファイル付きフルパイプライン
oss-paper-ci workbench . --output-dir results

# 安全な再現試行
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# CI統合
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

ワークフローテンプレートは [examples/github-actions/](examples/github-actions/) を参照。

## ドキュメント

| トピック | リンク |
|----------|--------|
| はじめに | [docs/getting-started.md](docs/getting-started.md) |
| CLIリファレンス | [docs/cli-reference.md](docs/cli-reference.md) |
| ターミナルワークベンチ | [docs/terminal-workbench.md](docs/terminal-workbench.md) |
| プロジェクト概要 | [docs/project-summary.md](docs/project-summary.md) |
| デモギャラリー | [docs/demo-gallery.md](docs/demo-gallery.md) |
| 完全な索引 | [docs/index.md](docs/index.md) |

## 制限事項

- 再現*準備度*をチェックするもので、科学的正しさをチェックするものではない
- 論文の品質、革新性、採択確率を判断しない
- 実験を実行しない（明示的に `--execute` を使用しない限り）
- 欠損データの解決や壊れたコードの修正はしない
- スコアはエンジニアリングの完全性の指標であり、科学的判断ではない

詳細は [docs/limitations.md](docs/limitations.md) を参照。

## 開発

```bash
pip install -e ".[dev]"
python -m pytest
python scripts/check_docs_truthfulness.py --check
```

## ライセンス

MIT — [LICENSE](LICENSE) を参照。
