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
# 1. GitHub からインストール
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e .

# 2. 60秒で試す
oss-paper-ci try-demo

# 3. リポジトリをスキャン
oss-paper-ci scan .
```

**他のインストール方法：** pipx、wheel、ソースインストールの詳細は [インストール](docs/installation.md) を参照。

> **注意：** oss-paper-ci はまだ PyPI で公開されていません。GitHub ソースからインストールしてください。

## 初回実行

```bash
# パーソナライズされた推奨事項を取得
oss-paper-ci quickstart

# トピック別のガイダンス
oss-paper-ci quickstart --topic install
oss-paper-ci quickstart --topic github-action
oss-paper-ci quickstart --topic reproduce
oss-paper-ci quickstart --topic eval
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
| 再現オーケストレーター | `oss-paper-ci reproduce plan/run/report` | 再現ワークフローの計画・実行・検証 |
| 再現カプセル | `oss-paper-ci capsule verify out.zip` | 証拠パッケージの検証と確認 |
| 再現ドシエ | `oss-paper-ci dossier .` | 著者/レビュアー/メンテナー向けの要約を生成 |
| ワークスペースバッチ | `oss-paper-ci batch scan --workspace ws.yml` | 設定ファイルから複数プロジェクトをスキャン |
| リポジトリ intake | `oss-paper-ci intake .` | リポジトリ構造の分析、コマンド抽出、エコシステム検出 |
| 自動プラン | `oss-paper-ci autoplan .` | リポジトリ分析から候補再現計画を生成 |
| エコシステム検出 | `oss-paper-ci ecosystems detect .` | Python、R、Julia、MATLABなどを検出 |
| ターミナルワークベンチ | `oss-paper-ci workbench .` | 進行状況表示付きマルチステップパイプライン |
| ウィザード | `oss-paper-ci wizard` | 新規ユーザー向けの安全な次のステップを提案 |
| 信頼監査 | `oss-paper-ci trust audit .` | ローカル静的信頼・ワークフロー監査 |
| セキュリティスキャン | `oss-paper-ci security scan .` | シークレット、危険パターン、Docker リスクをスキャン |
| 依存関係インベントリ | `oss-paper-ci trust inventory .` | SBOM 風依存関係インベントリ |
| プロベナンスマニフェスト | `oss-paper-ci trust provenance .` | ローカルプロベナンスマニフェストを生成 |
| 成果物検証 | `oss-paper-ci trust verify-artifacts .` | SHA256 チェックサムを検証 |

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

## 信頼とセキュリティ

OSS-Paper-CI は、ワークフロー権限、疑わしいシークレット、危険なスクリプトパターン、依存関係インベントリ、リリース成果物検物検証などのローカル静的チェックを行えます。ただし、これは安全認証ではなく、リポジトリが完全に安全であることを証明するものではありません。

```bash
# 信頼監査（ワークフローリスク、権限、アクションのピン留め）
oss-paper-ci trust audit .

# セキュリティスキャン（シークレット、危険パターン、Dockerリスク）
oss-paper-ci security scan .

# 依存関係インベントリ（SBOM風）
oss-paper-ci trust inventory .

# プロベナンスマニフェスト
oss-paper-ci trust provenance .

# リリース成果物の検証
oss-paper-ci trust verify-artifacts release-artifacts/
```

**重要な注意：** これらはローカル静的解析チェックのみです。安全認証ではなく、サードパーティの整合性を検証するものでもなく、SLSA、Sigstore、SPDX 準拠を主張するものでもありません。完全な脅威モデルと制限事項は [SECURITY.md](SECURITY.md) を参照してください。

## 統合エビデンスレポート

統合エビデンスレポートは、再現準備状況、環境、データ、結果、実行入口、信頼性チェック、安全境界を一つのレポートにまとめます。これは再現性の証拠を共有するためのものであり、論文の科学的正しさや採否を判定するものではありません。

```bash
# レビュアー向けレポート
oss-paper-ci evidence . --profile reviewer --format html --output evidence.html

# 著者向けレポート
oss-paper-ci evidence . --profile author --format markdown

# 共有可能なバンドルの作成
oss-paper-ci evidence bundle . --output evidence-bundle.zip

# バンドルの整合性検証
oss-paper-ci evidence verify evidence-bundle.zip
```

詳細は [docs/evidence-report.md](docs/evidence-report.md) を参照。

## 再現オーケストレーター

再現オーケストレーターは、リポジトリ内の `reproducibility.yml` を読み取り、実行計画を作成し、明示的な許可がある場合のみ宣言されたコマンドを実行し、ログ・成果物・指標を収集して再現レポートを生成します。デフォルトではコードを実行せず、論文の科学的正しさを証明するものではありません。

```bash
# 計画の生成（コードを実行しない）
oss-paper-ci reproduce plan examples/repro-system-demo

# 明示的な許可後に実行
oss-paper-ci reproduce run examples/repro-system-demo --execute --sandbox local

# HTMLレポートの生成
oss-paper-ci reproduce report .oss-paper-ci-repro-run --format html --output reproduction.html

# 期待値との比較
oss-paper-ci reproduce compare .oss-paper-ci-repro-run --expected examples/repro-system-demo/reproducibility.yml

# 証拠バンドルの作成
oss-paper-ci reproduce bundle .oss-paper-ci-repro-run --output reproduction-evidence.zip
```

詳細は [docs/reproduction-orchestrator.md](docs/reproduction-orchestrator.md) を参照。

## リポジトリ intake と自動プラン

多くの研究リポジトリには標準化された `reproducibility.yml` がありません。OSS-Paper-CI はリポジトリを分析し、README、環境ファイル、スクリプト、notebook、ワークフロー、結果ディレクトリから情報を抽出し、候補となる再現計画を生成できます。この計画は人間による確認が必要であり、推定されたコマンドはデフォルトでは実行されません。

```bash
# リポジトリの分析（読み取り専用）
oss-paper-ci intake .

# 候補再現計画の生成
oss-paper-ci autoplan . --output candidate-reproducibility.yml

# 候補計画の検証
oss-paper-ci autoplan validate candidate-reproducibility.yml

# 既存設定との比較
oss-paper-ci autoplan diff --old reproducibility.yml --new candidate-reproducibility.yml
```

詳細は [docs/repository-intake.md](docs/repository-intake.md) と [docs/autoplan.md](docs/autoplan.md) を参照。

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
