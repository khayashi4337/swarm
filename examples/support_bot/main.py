import re

import qdrant_client
from openai import OpenAI

from swarm import Agent
from swarm.repl import run_demo_loop

# 接続を初期化する
client = OpenAI()  # OpenAIクライアントの初期化
qdrant = qdrant_client.QdrantClient(host="localhost")  # Qdrantクライアントの初期化

# 埋め込みモデルの設定
EMBEDDING_MODEL = "text-embedding-3-large"

# Qdrantコレクションの設定
collection_name = "help_center"

# Qdrantにクエリを実行する関数
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

    # Qdrantに埋め込みベクトルを使って検索を実行
    query_results = qdrant.search(
        collection_name=collection_name,
        query_vector=(vector_name, embedded_query),
        limit=top_k,
    )

    return query_results

# 知識ベースから関連する記事を検索する関数
def query_docs(query):
    print(f"Searching knowledge base with query: {query}")  # クエリの表示
    query_results = query_qdrant(query, collection_name=collection_name)
    output = []

    # クエリ結果からタイトル、テキスト、URLを取得
    for i, article in enumerate(query_results):
        title = article.payload["title"]
        text = article.payload["text"]
        url = article.payload["url"]

        output.append((title, text, url))

    # 結果が存在する場合、最も関連する記事を返す
    if output:
        title, content, _ = output[0]
        response = f"Title: {title}\nContent: {content}"
        truncated_content = re.sub(
            r"\s+", " ", content[:50] + "..." if len(content) > 50 else content
        )
        print("Most relevant article title:", truncated_content)
        return {"response": response}
    else:
        print("No results")
        return {"response": "No results found."}

# ユーザーにメールを送信する関数
def send_email(email_address, message):
    response = f"Email sent to: {email_address} with message: {message}"
    return {"response": response}

# ユーザーのためにチケットを作成する関数
def submit_ticket(description):
    return {"response": f"Ticket created for {description}"}

# ユーザーをヘルプセンターエージェントに転送する関数
def transfer_to_help_center():
    return help_center_agent

# ユーザーインターフェースエージェントを定義
user_interface_agent = Agent(
    name="ユーザーインターフェースエージェント",
    instructions="ユーザーとのすべてのやり取りを処理するユーザーインターフェースエージェントです。一般的な質問や、他のエージェントが適さないユーザーのクエリに対応します。",
    functions=[transfer_to_help_center],
)

# ヘルプセンターエージェントを定義
help_center_agent = Agent(
    name="ヘルプセンターエージェント",
    instructions="OpenAI製品に関する質問に対応するヘルプセンターエージェントです。GPTモデル、DALL-E、Whisperなどについて扱います。",
    functions=[query_docs, submit_ticket, send_email],
)

if __name__ == "__main__":
    # デモループを実行してエージェントを起動
    run_demo_loop(user_interface_agent)
