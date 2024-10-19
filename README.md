こちらがSwarmのREADME.mdの日本語訳です。

![Swarm ロゴ](assets/logo.png)

# Swarm（実験的、教育用）

エルゴノミクスで軽量なマルチエージェントオーケストレーションを探索する教育的なフレームワーク。

> [!WARNING]
> Swarmは現在、エルゴノミクスなインターフェースの探索を目的とした実験的なサンプルフレームワークです。プロダクション環境での使用を想定していないため、公式なサポートはありません。（このため、PRや問題のレビューも行いません！）
>
> Swarmの主な目的は、[Orchestrating Agents: Handoffs & Routines](https://cookbook.openai.com/examples/orchestrating_agents)クックブックで紹介されているハンドオフとルーチンパターンを示すことです。スタンドアロンのライブラリとして使用することは想定されておらず、主に教育目的です。

## インストール

Python 3.10+ が必要です

```shell
pip install git+ssh://git@github.com/openai/swarm.git
```

または

```shell
pip install git+https://github.com/openai/swarm.git
```

## 使用方法

```python
from swarm import Swarm, Agent

client = Swarm()

def transfer_to_agent_b():
    return agent_b


agent_a = Agent(
    name="エージェントA",
    instructions="あなたは役に立つエージェントです。",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="エージェントB",
    instructions="俳句のみで話してください。",
)

response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "エージェントBと話したいです。"}],
)

print(response.messages[-1]["content"])
```

```
希望が明るく輝き、
新たな道が優雅に交わる、
どうお手伝いしましょうか？
```

## 目次

- [概要](#overview)
- [例](#examples)
- [ドキュメント](#documentation)
  - [Swarmの実行](#running-swarm)
  - [エージェント](#agents)
  - [関数](#functions)
  - [ストリーミング](#streaming)
- [評価](#evaluations)
- [ユーティリティ](#utils)

# 概要

Swarmは、エージェントの**コーディネーション**と**実行**を軽量で高度にコントロール可能で、簡単にテストできるようにすることを目的としています。

これを実現するために、Swarmでは2つの基本的な抽象概念を使用しています。それは`Agent`と**ハンドオフ**です。`Agent`は`instructions`と`tools`を包括し、任意のタイミングで会話を他の`Agent`にハンドオフすることができます。

これらのプリミティブは、ツールとエージェントのネットワーク間で豊富なダイナミクスを表現するのに十分な力を持ち、学習の負担を減らしながらスケーラブルな実用的ソリューションを構築することが可能です。

> [!NOTE]
> SwarmのエージェントはAssistants APIのアシスタントとは無関係です。同じ名前が付けられているのは利便性のためですが、それ以外は全く異なります。Swarmは完全にChat Completions APIを利用して動作しており、コール間で状態を保持しません。

## Swarmを選ぶ理由

Swarmは、軽量でスケーラブル、かつ高度にカスタマイズ可能なパターンを探索します。Swarmのようなアプローチは、多数の独立した機能や指示を1つのプロンプトにエンコードするのが困難な場合に最も適しています。

Assistants APIは完全にホストされたスレッドやメモリ管理・取得が組み込まれたものを探している開発者にとって素晴らしいオプションですが、Swarmはマルチエージェントオーケストレーションを学びたい開発者向けの教育リソースです。Swarmはクライアント側で（ほぼ）完全に動作し、Chat Completions APIと同様にコール間で状態を保存しません。

# 例

インスピレーションを得るために `/examples` をご覧ください！各例の詳細については、そのREADMEをご覧ください。

- [`basic`](examples/basic): セットアップ、関数呼び出し、ハンドオフ、コンテキスト変数などの基本的な例
- [`triage_agent`](examples/triage_agent): 正しいエージェントに引き継ぐための基本的なトリアージ手順を設定する簡単な例
- [`weather_agent`](examples/weather_agent): 関数呼び出しの簡単な例
- [`airline`](examples/airline): 航空会社のコンテキストで異なる顧客サービス要求を処理するためのマルチエージェント設定
- [`support_bot`](examples/support_bot): ユーザーインターフェースエージェントと複数のツールを持つヘルプセンターエージェントを含むカスタマーサービスボット
- [`personal_shopper`](examples/personal_shopper): 販売や返品の手続きを支援するパーソナルショッピングエージェント

# ドキュメント

![Swarm 図](assets/swarm_diagram.png)

## Swarmの実行

最初に、Swarmクライアントをインスタンス化します（内部的には`OpenAI`クライアントをインスタンス化するだけです）。

```python
from swarm import Swarm

client = Swarm()
```

### `client.run()`

Swarmの`run()`関数は、Chat Completions APIの`chat.completions.create()`関数に相当します。`messages`を受け取り、`messages`を返し、呼び出し間で状態を保存しません。しかし、`run()`はエージェントの関数実行、ハンドオフ、コンテキスト変数の参照を処理し、ユーザーに戻る前に複数回の対話を行うことができます。

Swarmの`client.run()`は以下のループを実装しています：

1. 現在のエージェントからの完了を取得
2. ツール呼び出しを実行し、結果を追加
3. 必要に応じてエージェントを切り替え
4. 必要に応じてコンテキスト変数を更新
5. 新しい関数呼び出しがなければ、結果を返す

#### 引数

| 引数                 | 型      | 説明                                                                                               | デフォルト        |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------ | -------------- |
| **agent**            | `Agent` | 呼び出される（最初の）エージェント                                                                 | （必須）        |
| **messages**         | `List`  | メッセージオブジェクトのリスト。[Chat Completions `messages`](https://platform.openai.com/docs/api-reference/chat/create#chat-create-messages)と同じ形式 | （必須）        |
| **context_variables**| `dict`  | 関数およびエージェントの指示に利用可能な追加のコンテキスト変数の辞書                                 | `{}`           |
| **max_turns**        | `int`   | 許容される対話の最大回数                                                                           | `float("inf")` |
| **model_override**   | `str`   | エージェントが使用するモデルを上書きするための任意の文字列                                         | `None`         |
| **execute_tools**    | `bool`  | `False`の場合、エージェントが関数を呼び出した際にツール呼び出しメッセージを直ちに返し、実行を中断  | `True`         |
| **stream**           | `bool`  | `True`の場合、ストリーミングレスポンスを有効にする                                                  | `False`        |
| **debug**            | `bool`  | `True`の場合、デバッグログを有効にする                                                              | `False`        |

`client.run()`が終了すると、関連する更新された状態をすべて含む`Response`を返します。具体的には、新しい`messages`、最後に呼び出された`Agent`、および最新の`context_variables`です。これらの値（および新しいユーザーメッセージ）を次回の`client.run()`の実行に渡すことで、前回のやりとりを続けることができます。(`run_demo_loop`関数は、`/swarm/repl/repl.py`でフル実行ループの例を実装しています。）

#### `Response` フィールド

| フィールド             | 型      | 説明                                                                                                                                                                                                                                                           |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **messages**         | `List`  | 対話中に生成されたメッセージオブジェクトのリスト。Chat Completionsの`messages`と非常に似ていますが、どの`Agent`からのメッセージかを示す`sender`フィールドが含まれています。                                                                                     |
| **agent**            | `Agent` | 最後にメッセージを処理したエージェント。                                                                                                                                                                                                                         |
| **context_variables**| `dict`  | 入力変数と同じですが、必要に応じて変更されたものです。                                                                                                                                                                                                          |

## エージェント

`Agent`は単に`instructions`と`functions`をセットにしたもので、他の`Agent`に実行をハンドオフする能力を持ちます。
