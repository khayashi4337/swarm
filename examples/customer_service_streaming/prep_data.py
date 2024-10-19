import os
import json
from openai import OpenAI

# OpenAI クライアントのインスタンスを作成
client = OpenAI()
GPT_MODEL = 'gpt-4'
EMBEDDING_MODEL = "text-embedding-3-large"

# 記事リストの読み込み
# ディレクトリ 'data' から記事ファイルのリストを取得
article_list = os.listdir('data')

articles = []

# 各記事の JSON ファイルを開き、データを読み込む
# 'data' フォルダ内の各ファイルを順に処理
for article in article_list:
    article_path = 'data/' + article

    # JSON ファイルを開く
    f = open(article_path)

    # JSON オブジェクトを辞書として読み込む
    data = json.load(f)

    articles.append(data)

    # ファイルを閉じる
    f.close()

# 各記事に対して埋め込みベクトルを生成し、追加
# 記事の内容から埋め込みベクトルを生成し、各記事に追加
for i, article in enumerate(articles):
    try:
        embedding = client.embeddings.create(model=EMBEDDING_MODEL, input=article['text'])
        articles[i].update({"embedding": embedding.data[0].embedding})
    except Exception as e:
        # 埋め込みの生成に失敗した場合、タイトルとエラー内容を出力
        print(article['title'])
        print(e)

import qdrant_client
from qdrant_client.http import models as rest
import pandas as pd

# Qdrant クライアントの作成
# ローカルホスト上で Qdrant データベースに接続
qdrant = qdrant_client.QdrantClient(host='localhost')
qdrant.get_collections()

# コレクション名の設定
collection_name = 'help_center'

# ベクトルサイズを取得
# 記事の埋め込みベクトルのサイズを取得
vector_size = len(articles[0]['embedding'])

# 記事のデータフレームを作成
# 記事のリストをデータフレームに変換
article_df = pd.DataFrame(articles)
article_df.head()

# ベクトルデータベースのコレクションを作成
# Qdrant に新しいコレクションを作成し、ベクトルの設定を定義
qdrant.recreate_collection(
    collection_name=collection_name,
    vectors_config={
        'article': rest.VectorParams(
            distance=rest.Distance.COSINE,  # コサイン距離を使用して類似度を計算
            size=vector_size,
        )
    }
)

# ベクトルでコレクションを埋める
# 記事の埋め込みベクトルを Qdrant にアップサートしてコレクションに追加
qdrant.upsert(
    collection_name=collection_name,
    points=[
        rest.PointStruct(
            id=key,  # 各記事のキーとしてインデックスを使用
            vector={
                'article': value['embedding'],  # 埋め込みベクトルを設定
            },
            payload=value.to_dict(),  # 記事の内容をペイロードとして追加
        )
        for key, value in article_df.iterrows()
    ],
)
