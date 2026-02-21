# セットアップガイド

Ubuntu 24.04 での環境構築手順。

## 前提条件

- Ubuntu 24.04 LTS
- sudo 権限
- インターネット接続
- vJunos-router QCOW2 イメージ

## 自動セットアップ

```bash
sudo bash setup/install.sh
```

このスクリプトは以下をインストールします:
1. **Docker** - コンテナ実行環境
2. **containerlab** - ネットワークラボオーケストレータ
3. **FRR イメージ** - `quay.io/frrouting/frr:10.3.1`
4. **vrnetlab** - vJunos QCOW2 → Docker イメージ変換
5. **Python 3** - mcp-bridge 実行環境

## vJunos-router イメージの準備

### 1. ダウンロード
[Juniper サポートサイト](https://support.juniper.net/) から `vJunos-router-*.qcow2` をダウンロード。

### 2. 配置
```bash
cp vJunos-router-25.4R1.12.qcow2 images/
```

### 3. Docker イメージビルド
`setup/install.sh` を実行すると自動で vrnetlab によるビルドが行われます。  
手動で行う場合:

```bash
cp images/vJunos-router-25.4R1.12.qcow2 /opt/vrnetlab/vjunos-router/
cd /opt/vrnetlab/vjunos-router
sudo make
```

### 4. 確認
```bash
docker images | grep vjunos
# vrnetlab/vr-vjunos   25.4R1.12   ...
```

## mcp-bridge のセットアップ

```bash
cd mcp-bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 動作確認

```bash
# ラボデプロイ
sudo clab deploy -t labs/basic-bgp/topology.clab.yml

# ノード確認
sudo clab inspect -t labs/basic-bgp/topology.clab.yml

# BGP 確認
docker exec clab-basic-bgp-frr1 vtysh -c "show ip bgp summary"
docker exec clab-basic-bgp-vjunos1 cli show bgp summary
```
