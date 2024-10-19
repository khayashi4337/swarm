import json
import os

import pandas as pd
import qdrant_client
from openai import OpenAI
from qdrant_client.http import models as rest

# OpenAIクライアントの初期化
client = OpenAI()
GPT_MODEL = "gpt-4o"
EMBEDDING_MODEL = "text-embedding-3-large"

# データディレクトリから記事リストを取得
article_list = os.listdir("data")

# 記事の内容を格納するリスト
articles = []

# 各記事を読み込み、リストに追加
for article_filename in article_list:
    # 記事のパスを取得
    article_path = "data/" + article_filename

    # JSONファイルを開く
    with open(article_path) as json_file:
        # JSONオブジェクトを辞書として読み込む
        data = json.load(json_file)
        articles.append(data)

# 各記事に対して埋め込みベクトルを生成し、追加
for index, article in enumerate(articles):
    try:
        # 記事のテキストを使って埋め込みベクトルを生成
        embedding = client.embeddings.create(model=EMBEDDING_MODEL, input=article["text"])
        articles[index].update({"embedding": embedding.data[0].embedding})
    except Exception as e:
        # エラーが発生した場合、記事のタイトルとエラーメッセージを出力
        print(article["title"])
        print(e)

# Qdrantクライアントの初期化
qdrant = qdrant_client.QdrantClient(host="localhost")
qdrant.get_collections()

# コレクション名の設定
collection_name = "help_center"

# ベクトルのサイズを取得
vector_size = len(articles[0]["embedding"])

# 記事データをDataFrameに変換
article_df = pd.DataFrame(articles)
article_df.head()

# コレクションが存在する場合、削除して再作成（記事の変更を反映するため）
if qdrant.get_collection(collection_name=collection_name):
    qdrant.delete_collection(collection_name=collection_name)

# ベクトルDBコレクションを作成
qdrant.create_collection(
    collection_name=collection_name,
    vectors_config={
        "article": rest.VectorParams(
            distance=rest.Distance.COSINE,  # コサイン距離を使用してベクトル間の類似度を測定
            size=vector_size,  # ベクトルのサイズを設定
        )
    },
)

# ベクトルでコレクションを埋める
qdrant.upsert(
    collection_name=collection_name,
    points=[
        rest.PointStruct(
            id=index,  # 各ポイントにユニークなIDを割り当てる
            vector={
                "article": row["embedding"],  # 記事の埋め込みベクトルを設定
            },
            payload=row.to_dict(),  # 各記事の内容をペイロードとして格納
        )
        for index, row in article_df.iterrows()  # DataFrameの各行を反復処理
    ],
)
