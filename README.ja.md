# oss-paper-ci

[English](README.md) | [简体中文](README.zh-CN.md) | **日本語**

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

科学リポジトリの再現準備度チェック、再現試行、再現カプセル作成のためのCLIツールセット。

## 機能

- **scan** — リポジトリの再現準備度をチェック（環境ファイル、スクリプト、データ文書、CI設定）
- **reproduce** — リポジトリのクローン、依存関係のインストール、コマンドの実行（デフォルトは安全モード：dry-run）
- **capsule** — 再現試行を検証可能な証拠パッケージにパッケージ化
- **batch** — 複数プロジェクトの一括スキャン
- **guide** — ロールとトピックに基づいたガイド付きヘルプ

## インストール

```bash
# ソースからインストール（開発向け）
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# インストールの確認
oss-paper-ci version
```

## 3つの基本コマンド

```bash
# 1. リポジトリをスキャン
oss-paper-ci scan examples/demo-paper-repo --format markdown

# 2. 再現を試行（安全モード：デフォルトではコードを実行しない）
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# 3. 再現カプセルを検証
oss-paper-ci capsule verify repro-capsule.zip
```

## クイックスタート

```bash
# リポジトリをスキャン
oss-paper-ci scan /path/to/your/repo

# HTMLレポートを生成
oss-paper-ci scan . --format html --output report.html

# GitHub Actionsで使用
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

## ワンコマンド再現試行

```bash
# 安全モード：何が起きるか確認（コードは実行しない）
oss-paper-ci reproduce https://github.com/owner/paper-repo --dry-run

# 実行モード：クローン、インストール、実行、レポート生成
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --format html --output repro-report.html

# 検証可能な再現カプセルを生成
oss-paper-ci reproduce examples/demo-reproduce-repo \
  --execute --install --capsule repro-capsule.zip
```

reproduceコマンドはリポジトリをクローンし、環境ファイルを検出し、
依存関係をインストールし（隔離された仮想環境内で）、再現コマンドを実行し、
構造化レポートを生成します。デフォルトモードはdry-runです。
実際にコードを実行するには`--execute`が必要です。

**重要：** これは*再現試行*であり、再現成功の保証ではありません。
ツールは実行した内容を記録するもので、結果が正しいことを証明するものではありません。

## 再現カプセル

```bash
# カプセルの完全性を検証
oss-paper-ci capsule verify repro-capsule.zip

# カプセルの内容を確認
oss-paper-ci capsule inspect repro-capsule.zip

# 2つのカプセルを比較
oss-paper-ci capsule diff old.zip new.zip
```

再現カプセルは、マニフェスト、レポート、ログ、メタデータ、
SHA256完全性チェックサムを含む自己完結型の証拠パッケージです。
これは論文の正しさの証明**ではありません**。

## ガイドモード

```bash
# ガイド付きヘルプを取得
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

## ドキュメント

| トピック | リンク |
|----------|--------|
| はじめに | [docs/getting-started.md](docs/getting-started.md) |
| インストール | [docs/installation.md](docs/installation.md) |
| CLIリファレンス | [docs/cli-reference.md](docs/cli-reference.md) |
| セキュリティモデル | [docs/security-model.md](docs/security-model.md) |
| 失敗分類 | [docs/failure-taxonomy.md](docs/failure-taxonomy.md) |
| 用語集 | [docs/glossary.md](docs/glossary.md) |
| ロールガイド | [docs/roles.md](docs/roles.md) |
| 再現 | [docs/reproduce.md](docs/reproduce.md) |
| 再現カプセル | [docs/reproduction-capsules.md](docs/reproduction-capsules.md) |
| 制限事項 | [docs/limitations.md](docs/limitations.md) |
| 完全な索引 | [docs/index.md](docs/index.md) |

## セキュリティモデル

- デフォルトモードは**dry-run**：コードは実行されず、依存関係はインストールされない
- `--execute`で再現コマンドが実行される
- `--install`で依存関係がインストールされる（隔離された仮想環境内）
- 危険なコマンドはブロックされる（rm -rf、sudo、fork bombなど）
- すべてのコマンドに設定可能なタイムアウトがある

## 制限事項

- 再現*準備度*をチェックするもので、科学的正しさをチェックするものではない
- 論文の品質、革新性、採択確率を判断しない
- 実験を実行しない（明示的に`--execute`を使用しない限り）
- 欠損データの解決や壊れたコードの修正はしない
- Python以外のクロス言語チェックは浅い
- スコアはエンジニアリングの完全性の指標であり、科学的判断ではない

## 失敗も情報

再現試行が失敗した場合、失敗レポート自体が有价值的な再現証拠です。
何を試みたか、どこで失敗したか、環境がどうであったかを記録します。
失敗は論文に問題があることを意味しません — 環境や依存関係の問題かもしれません。

詳細は [docs/failure-taxonomy.md](docs/failure-taxonomy.md) を参照してください。

## 開発

```bash
pip install -e ".[dev]"
python -m pytest
python -m build
python -m twine check dist/*
python scripts/check_docs_truthfulness.py --check
```

## ライセンス

MIT — [LICENSE](LICENSE)を参照。
