# Labs

containerlab トポロジ定義と初期設定ファイル。

## 利用可能なラボ

### basic-bgp
FRR + vJunos-router の最小 eBGP 構成。

```
FRR1 (AS65001, 192.0.2.1/30) ---- P2P ---- vJunos1 (AS65002, 192.0.2.2/30)
     Lo: 10.0.0.1/32                         Lo: 10.0.0.2/32
```

```bash
# デプロイ
sudo clab deploy -t labs/basic-bgp/topology.clab.yml

# 確認
sudo clab inspect -t labs/basic-bgp/topology.clab.yml

# 破棄
sudo clab destroy -t labs/basic-bgp/topology.clab.yml
```
