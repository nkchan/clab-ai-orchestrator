# トラブルシューティング

## containerlab 関連

### `clab deploy` が失敗する

**症状**: Permission denied エラー

```bash
# sudo で実行する
sudo clab deploy -t labs/basic-bgp/topology.clab.yml
```

### vJunos ノードが起動しない

**症状**: `clab inspect` でノードが `running` にならない

1. Docker イメージの確認:
```bash
docker images | grep vjunos
```

2. イメージが無い場合は vrnetlab でビルド:
```bash
cp images/vJunos-router-25.4R1.12.qcow2 /opt/vrnetlab/vjunos-router/
cd /opt/vrnetlab/vjunos-router && sudo make
```

3. vJunos は起動に **3〜5分** かかる場合があります。しばらく待ってから再確認してください。

### ラボが残っている

```bash
# 状態確認
sudo clab inspect --all

# 特定ラボの破棄
sudo clab destroy -t labs/basic-bgp/topology.clab.yml

# クリーンアップ付き
sudo clab destroy -t labs/basic-bgp/topology.clab.yml --cleanup
```

## BGP 関連

### BGP ネイバーが Established にならない

1. **IP アドレス確認**:
```bash
# FRR
docker exec clab-basic-bgp-frr1 vtysh -c "show interface brief"

# vJunos
docker exec clab-basic-bgp-vjunos1 cli show interfaces terse
```

2. **疎通確認**:
```bash
docker exec clab-basic-bgp-frr1 ping -c 3 192.0.2.2
```

3. **BGP 詳細ログ**:
```bash
# FRR
docker exec clab-basic-bgp-frr1 vtysh -c "show ip bgp neighbor 192.0.2.2"

# vJunos
docker exec clab-basic-bgp-vjunos1 cli show bgp neighbor 192.0.2.1
```

## mcp-bridge 関連

### インストールエラー

```bash
cd mcp-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### MCP サーバが起動しない

- Python 3.10 以上が必要です
- `mcp` パッケージが正しくインストールされているか確認:
```bash
pip show mcp
```
