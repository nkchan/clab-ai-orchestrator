# Sample 03: Config Change

Jinja2 テンプレートを使って設定を生成し、FRR / vJunos に投入するシナリオ。

## シナリオ概要

既存の BGP 設定に加えて、新しい Loopback ネットワークを追加広告します。

```
変更前: FRR1 → 10.0.0.1/32 のみ広告
変更後: FRR1 → 10.0.0.1/32 + 10.1.0.0/24 を広告
```

## 手順

### Step 1: 現在の経路を確認

```json
{
  "tool": "junos_show",
  "arguments": {
    "container_name": "clab-basic-bgp-vjunos1",
    "command": "show route receive-protocol bgp 192.0.2.1"
  }
}
```

**期待される出力:** 10.0.0.1/32 のみ

### Step 2: テンプレートで設定を生成

```python
# vendors/frr/templates を使った設定生成の例
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("vendors/frr/templates"))

# 追加ネットワーク用のカスタムテンプレートも作成可能
config_lines = [
    "router bgp 65001",
    "address-family ipv4 unicast",
    "network 10.1.0.0/24",
    "exit-address-family",
]
```

### Step 3: FRR に設定を投入

**MCP ツール:**
```json
{
  "tool": "frr_config",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "config_commands": [
      "interface lo",
      "ip address 10.1.0.1/24",
      "exit",
      "router bgp 65001",
      "address-family ipv4 unicast",
      "network 10.1.0.0/24",
      "exit-address-family"
    ]
  }
}
```

### Step 4: 広告を確認

```json
{
  "tool": "frr_show",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "command": "show ip bgp"
  }
}
```

### Step 5: vJunos 側で受信を確認

```json
{
  "tool": "junos_show",
  "arguments": {
    "container_name": "clab-basic-bgp-vjunos1",
    "command": "show route receive-protocol bgp 192.0.2.1"
  }
}
```

**期待される出力:** 10.0.0.1/32 + 10.1.0.0/24

### Step 6: ロールバック

設定を元に戻す。

```json
{
  "tool": "frr_config",
  "arguments": {
    "container_name": "clab-basic-bgp-frr1",
    "config_commands": [
      "interface lo",
      "no ip address 10.1.0.1/24",
      "exit",
      "router bgp 65001",
      "address-family ipv4 unicast",
      "no network 10.1.0.0/24",
      "exit-address-family"
    ]
  }
}
```

## 学べること

- Jinja2 テンプレートを使った設定生成
- ネットワーク追加広告の流れ
- FRR / Junos 間での経路伝搬確認
- 設定のロールバック方法
