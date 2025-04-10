import sqlite3

DATABASE = 'database.db'

def create_books_table():
  con = sqlite3.connect(DATABASE)
  con.execute("""
    CREATE TABLE IF NOT EXISTS books (
      id INTEGER PRIMARY KEY AUTOINCREMENT,  -- id自動割り振り
      title TEXT NOT NULL,
      price INTEGER NOT NULL,
      arrival_day TEXT NOT NULL,
      author TEXT NOT NULL,
      stock INTEGER NOT NULL,  -- 在庫
      deleted_at TEXT
    )
  """)
  con.close()

def create_orders_table():
  con = sqlite3.connect(DATABASE)
  con.execute("""
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,  -- id自動割り振り
      book_id INTEGER NOT NULL,
      volume INTEGER NOT NULL,
      total_price INTEGER NOT NULL,
      ordered_at TEXT NOT NULL,
      FOREIGN KEY (book_id) REFERENCES books(id)  -- 外部キー制約をつける
    )
  """)
  con.close()


