# Open WebUI 連携サンプルプロンプト

Open WebUI に `mcp-bridge` (SSE通信) を設定した後、AIアシスタントに何を頼めばよいか迷った際にお使いいただけるプロンプトのサンプルです。
以下の文章をコピーしてチャット欄に貼り付けてみてください。

## 1. トポロジーの概要を確認（Deploy済みの場合）

```text
現在起動している basic-bgp ラボ (labs/basic-bgp/topology.clab.yml) の構成と、各ノードのステータス情報を教えてください。
```

## 2. BGP のステータスを確認

```text
basic-bgp ラボ内の frr1 と frr2 の間でBGPピアが構成されています。
それぞれのコンテナで `show ip bgp summary` コマンドを実行して、BGPが Established (経路が交換されている状態) になっているか確認して報告してください。
```

## 3. コンフィグの投入 (設定変更テスト)

```text
frr1 (コンテナ名: clab-basic-bgp-frr1) にログインし、以下の新しいLoopbackインターフェースのIPアドレス (10.10.10.1/32) を設定し、BGPで広報する設定を追加してください。

設定コマンド例:
configure terminal
interface lo
 ip address 10.10.10.1/32
exit
router bgp 65001
 address-family ipv4 unicast
  network 10.10.10.1/32
 exit-address-family
exit
```

## 4. トラブルシューティングのデモ（わざと設定を間違えた場合など）

```

## 5. 自律 agent のワークフロー検証 (Phase 2)

MCP の Prompts 機能により提供されるエンジニアのガイドライン（`agent.md`）を読み込ませた状態で、自律的にトラブルシューティングを任せるデモです。
チャット入力欄で `/agent` や `/mcp` などと入力し、プロンプトを挿入してから以下の指示を与えてください。（もしくは「システムプロンプト」欄に agent.md の内容を設定します）

```text
あなたは自律的なネットワークエンジニアです。上記 (agent.md) のガイドラインと「Plan → Act → Reflect → Document」のサイクルに従って、vjunos-test ラボの機器に異常がないか自律的に調査してください。調査には MCP のツールを使用してください。
```
