# MCP Bridge

containerlab / FRR / vJunos-router を操作するための MCP (Model Context Protocol) サーバ。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 起動

```bash
# STDIO モード
mcp-bridge
```

## 提供ツール

| ツール | 説明 |
|--------|------|
| `clab_deploy` | containerlab トポロジをデプロイ |
| `clab_destroy` | トポロジを破棄 |
| `clab_inspect` | ノード状態を確認 |
| `frr_show` | FRR で show コマンドを実行 |
| `frr_config` | FRR に設定を投入 |
| `junos_show` | vJunos で show コマンドを実行 |
| `junos_config` | vJunos に設定を投入 |

## 開発

```bash
# lint
ruff check src/

# テスト
pytest
```
