import sqlite3

# グローバル接続用変数
conn = None

# データベース接続を取得する関数
def get_connection():
    global conn
    if conn is None:
        # SQLite データベースに接続
        conn = sqlite3.connect("application.db")
    return conn

# データベースを作成する関数
def create_database():
    # SQLite データベースに接続
    conn = get_connection()
    cursor = conn.cursor()

    # Users テーブルを作成
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE,
            phone TEXT
        )
    """
    )

    # PurchaseHistory テーブルを作成
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS PurchaseHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date_of_purchase TEXT,
            item_id INTEGER,
            amount REAL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """
    )

    # Products テーブルを作成
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            price REAL NOT NULL
        );
        """
    )

    # 変更を保存
    conn.commit()

# ユーザーを追加する関数
def add_user(user_id, first_name, last_name, email, phone):
    conn = get_connection()
    cursor = conn.cursor()

    # ユーザーが既に存在するか確認
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        return

    try:
        # ユーザー情報を Users テーブルに挿入
        cursor.execute(
            """
            INSERT INTO Users (user_id, first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, first_name, last_name, email, phone),
        )
        # 変更を保存
        conn.commit()
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")

# 購入履歴を追加する関数
def add_purchase(user_id, date_of_purchase, item_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    # 購入履歴が既に存在するか確認
    cursor.execute(
        """
        SELECT * FROM PurchaseHistory
        WHERE user_id = ? AND item_id = ? AND date_of_purchase = ?
    """,
        (user_id, item_id, date_of_purchase),
    )
    if cursor.fetchone():
        return

    try:
        # 購入情報を PurchaseHistory テーブルに挿入
        cursor.execute(
            """
            INSERT INTO PurchaseHistory (user_id, date_of_purchase, item_id, amount)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, date_of_purchase, item_id, amount),
        )
        # 変更を保存
        conn.commit()
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")

# 商品を追加する関数
def add_product(product_id, product_name, price):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 商品情報を Products テーブルに挿入
        cursor.execute(
            """
        INSERT INTO Products (product_id, product_name, price)
        VALUES (?, ?, ?);
        """,
            (product_id, product_name, price),
        )
        # 変更を保存
        conn.commit()
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")

# データベース接続を閉じる関数
def close_connection():
    global conn
    if conn:
        conn.close()
        conn = None

# 指定したテーブルの内容をプレビューする関数
def preview_table(table_name):
    conn = sqlite3.connect("application.db")  # データベース名に接続
    cursor = conn.cursor()

    # 指定したテーブルから最初の5行を取得
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")

    rows = cursor.fetchall()

    # 各行を出力
    for row in rows:
        print(row)

    conn.close()

# データベースを初期化してデータをロードする関数
def initialize_database():
    global conn

    # データベーステーブルを初期化
    create_database()

    # 初期ユーザーを追加
    initial_users = [
        (1, "Alice", "Smith", "alice@test.com", "123-456-7890"),
        (2, "Bob", "Johnson", "bob@test.com", "234-567-8901"),
        (3, "Sarah", "Brown", "sarah@test.com", "555-567-8901"),
    ]

    for user in initial_users:
        add_user(*user)

    # 初期購入履歴を追加
    initial_purchases = [
        (1, "2024-01-01", 101, 99.99),
        (2, "2023-12-25", 100, 39.99),
        (3, "2023-11-14", 307, 49.99),
    ]

    for purchase in initial_purchases:
        add_purchase(*purchase)

    # 初期商品を追加
    initial_products = [
        (7, "Hat", 19.99),
        (8, "Wool socks", 29.99),
        (9, "Shoes", 39.99),
    ]

    for product in initial_products:
        add_product(*product)
