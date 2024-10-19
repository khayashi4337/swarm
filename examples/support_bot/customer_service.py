import re

import qdrant_client
from openai import OpenAI

from swarm import Agent
from swarm.repl import run_demo_loop

# 接続の初期化
client = OpenAI()  # OpenAIクライアントを初期化
qdrant = qdrant_client.QdrantClient(host="localhost")  # Qdrantクライアントをローカルホストで初期化

# 埋め込みモデルの設定
EMBEDDING_MODEL = "text-embedding-3-large"

# Qdrantのコレクション名を設定
collection_name = "help_center"

# Qdrantでの検索を行う関数
def query_qdrant(query, collection_name, vector_name="article", top_k=5):
    # ユーザーのクエリから埋め込みベクトルを作成
    embedded_query = (
        client.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL,
        )
        .data[0]
        .embedding
    )

    # Qdrantに対して検索を実行
    query_results = qdrant.search(
        collection_name=collection_name,
        query_vector=(vector_name, embedded_query),
        limit=top_k,
    )

    return query_results

# ドキュメントを検索する関数
def query_docs(query):
    print(f"ナレッジベースで検索を行います: {query}")
    query_results = query_qdrant(query, collection_name=collection_name)
    output = []

    # 検索結果を処理してリストに格納
    for i, article in enumerate(query_results):
        title = article.payload["title"]
        text = article.payload["text"]
        url = article.payload["url"]

        output.append((title, text, url))

    if output:
        # 最も関連性の高い記事のタイトルと内容を返す
        title, content, _ = output[0]
        response = f"タイトル: {title}\n内容: {content}"
        truncated_content = re.sub(
            r"\s+", " ", content[:50] + "..." if len(content) > 50 else content
        )
        print("最も関連性の高い記事のタイトル:", truncated_content)
        return {"response": response}
    else:
        print("結果が見つかりません")
        return {"response": "結果が見つかりませんでした。"}

# 顧客にメールを送信する関数
def send_email(email_address, message):
    response = f"{email_address} にメールを送信しました。内容: {message}"
    return {"response": response}

# サポートチケットを作成する関数
def submit_ticket(description):
    return {"response": f"{description} のサポートチケットを作成しました"}

# ユーザーインターフェースエージェントを定義
user_interface_agent = Agent(
    name="ユーザーインターフェースエージェント",
    instructions="あなたはユーザーインターフェースエージェントです。ユーザーとのすべてのやり取りを処理します。特定のエージェントが適さない場合は、このエージェントを使用します。",
    functions=[query_docs, submit_ticket, send_email],
)

# ヘルプセンターエージェントを定義
help_center_agent = Agent(
    name="ヘルプセンターエージェント",
    instructions="あなたはOpenAIのヘルプセンターエージェントです。GPTモデル、DALL-E、WhisperなどOpenAI製品に関する質問に対応します。",
    functions=[query_docs, submit_ticket, send_email],
)

# ユーザーをヘルプセンターに転送する関数
def transfer_to_help_center():
    """ユーザーをヘルプセンターエージェントに転送する関数。"""
    return help_center_agent

# ユーザーインターフェースエージェントに転送機能を追加
user_interface_agent.functions.append(transfer_to_help_center)

if __name__ == "__main__":
    # デモループを実行
    run_demo_loop(user_interface_agent)
