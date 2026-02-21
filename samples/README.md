# Samples - 使用例・シナリオ集

本ディレクトリには、Clab AI Orchestrator の具体的な使い方をシナリオ別にまとめています。  
各シナリオは独立しており、順番に実行することでプロジェクトの全機能を体験できます。

## シナリオ一覧

| # | シナリオ | 内容 | 対象ツール |
|---|---------|------|-----------|
| 01 | [Deploy & Verify](01_deploy_and_verify/) | ラボの構築から BGP 疎通確認まで | `clab_deploy`, `clab_inspect`, `frr_show`, `junos_show` |
| 02 | [Troubleshoot BGP](02_troubleshoot_bgp/) | BGP 障害の調査と修復 | `frr_show`, `junos_show`, `frr_config`, `junos_config` |
| 03 | [Config Change](03_config_change/) | 設定変更とロールバック | `frr_config`, `junos_config`, テンプレート |

## 前提条件

- `sudo clab deploy -t labs/basic-bgp/topology.clab.yml` でラボがデプロイ済み
- BGP が Established 状態

## 使い方

各シナリオの `README.md` に手順が記載されています。  
MCP ツール経由（AI エージェント）でも、手動の CLI でも実行できます。
