# Vendors

ベンダー固有のパーサと設定テンプレートを格納するモジュール。

## 構造

```
vendors/
├── frr/
│   ├── parser.py          # FRR show コマンド出力パーサ
│   └── templates/
│       └── bgp.conf.j2    # BGP 設定テンプレート
└── junos/
    ├── parser.py          # Junos show コマンド出力パーサ
    └── templates/
        └── bgp.conf.j2    # BGP 設定テンプレート
```

## パーサ

### FRR (`frr/parser.py`)
- `parse_bgp_summary()` - `show ip bgp summary` の出力を構造化
- `parse_ip_route()` - `show ip route` の出力を構造化

### Junos (`junos/parser.py`)
- `parse_bgp_summary()` - `show bgp summary` の出力を構造化 (text/JSON)
- `parse_route_table()` - `show route` の出力を構造化

## テンプレート

Jinja2 形式の設定テンプレート。新しいラボ構成を作成する際に使用。

### 使用例
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("vendors/frr/templates"))
template = env.get_template("bgp.conf.j2")
config = template.render(
    hostname="frr1",
    router_id="10.0.0.1",
    local_as=65001,
    neighbor_ip="192.0.2.2",
    remote_as=65002,
    loopback_ip="10.0.0.1/32",
    p2p_ip="192.0.2.1/30",
    p2p_interface="eth1",
)
```

## 新しいベンダーの追加

1. `vendors/<vendor_name>/` ディレクトリを作成
2. `parser.py` に show コマンドパーサを実装
3. `templates/` に Jinja2 テンプレートを追加
4. `mcp-bridge/src/mcp_bridge/tools/` に対応ツールを追加
