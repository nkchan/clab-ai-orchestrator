# バージョン管理戦略

本プロジェクトで使用するツール・ライブラリのバージョン固定方針。

## 方針

| レイヤー | 方式 | 理由 |
|---------|------|------|
| **Python ランタイム** | Dockerfile で固定 (`3.12.8`) | OS の Python に依存しない |
| **Python パッケージ** | `requirements.lock` で全ピン | 再現可能なビルド |
| **containerlab** | setup スクリプトで最新安定版 | 破壊的変更が少ない |
| **FRR イメージ** | `.env.example` でタグ固定 (`10.3.1`) | NOS バージョンは検証済みのものを使用 |
| **vJunos イメージ** | vrnetlab ビルド時に固定 (`25.4R1.12`) | イメージ単位で管理 |

## mcp-bridge: ネイティブ vs コンテナ

### コンテナ実行（推奨）

```bash
docker compose up -d
```

**メリット:**
- Python バージョン・依存関係が完全に分離される
- ホスト環境を汚さない
- Docker socket マウントで containerlab 操作も可能
- 本番環境とテスト環境で同一イメージが使える

**注意:**
- Docker socket を Read-Only でマウント → セキュリティ面の考慮
- STDIO 通信は `stdin_open: true` + `tty: true` で確保

### ネイティブ実行（開発時）

```bash
cd mcp-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
pip install -e ".[dev]"
mcp-bridge
```

開発中の素早いイテレーションにはネイティブ実行が便利。

## バージョン更新手順

### Python パッケージの更新

```bash
cd mcp-bridge
# 1. pyproject.toml の依存を編集
# 2. ロックファイルを再生成
pip install pip-tools
pip-compile pyproject.toml -o requirements.lock
# 3. テスト
pip install -r requirements.lock
pytest
# 4. Docker イメージを再ビルド
docker compose build
```

### FRR / vJunos イメージの更新

1. `.env.example` のバージョンタグを変更
2. `labs/` のトポロジ定義を新バージョンに合わせて更新
3. `samples/` で動作確認
