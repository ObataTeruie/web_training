from flaskr import app
from flask import render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
DATABASE = 'database.db'

### indexアクション
@app.route('/')
def index():
  con = sqlite3.connect(DATABASE)

  db_books = con.execute('SELECT * FROM books WHERE deleted_at IS NULL').fetchall()
  db_orders = con.execute('SELECT * FROM orders').fetchall()
  con.close()

  books = []
  for row in db_books:
    books.append({
      'id': row[0], 'title': row[1], 'price': row[2], 'arrival_day': row[3],
      'author': row[4], 'stock': row[5], 'deleted_at': row[6]
    })

  orders = []
  for row in db_orders:
    orders.append({
      'book_id': row[1], 'volume': row[2], 'total_price': row[3], 'ordered_at': row[4]
    })

  # booksとordersを関連付ける
  order_details = []
  for order in orders:
    ordered_book = next((book for book in books if book['id'] == order['book_id']), None)
    if ordered_book:
      order_details.append({
        'ordered_at': order['ordered_at'],
        'title': ordered_book['title'],
        'volume': order['volume'],
        'total_price': order['total_price']
      })

  return render_template('index.html', books=books, order_details=order_details)

### formアクション
@app.route('/form')
def form():
  error_message = request.args.get('error_message')
  return render_template(
    'form.html', 
    error_message=error_message
  )

### registerアクション
@app.route('/register', methods=['POST'])
def register():
  con = sqlite3.connect(DATABASE)

  title = request.form['title']
  price = request.form['price']
  arrival_day = request.form['arrival_day']
  author = request.form['author']
  stock = request.form['stock']
  deleted_at = None

  # バリデーション：必要なフィールドが空でないことをチェック
  if not title or not price or not arrival_day or not author or not stock:
    return redirect(url_for('form', error_message='全ての必須項目を入力してください'))

  con.execute('INSERT INTO books (title, price, arrival_day, author, stock, deleted_at) VALUES (?, ?, ?, ?, ?, ?)',
              [title, price, arrival_day, author, stock, deleted_at])
  con.commit()
  con.close()

  return redirect(url_for('index'))

### showアクション
@app.route('/show/<int:id>')
def show(id):
  con = sqlite3.connect(DATABASE)
  book = con.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
  con.close()

  if book is None:
    return "本が見つかりませんでした", 404

  book_data = {
    'id': book[0],
    'title': book[1],
    'price': book[2],
    'arrival_day': book[3],
    'author': book[4],
    'stock': book[5],
  }

  return render_template(
    'show.html', book=book_data
  )

### editアクション
@app.route('/edit/<int:id>')
def edit(id):
  con = sqlite3.connect(DATABASE)
  row = con.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
  con.close()

  if row is None:
      return '本が見つかりませんでした', 404

  book = {
    'id': row[0],
    'title': row[1],
    'price': row[2],
    'arrival_day': row[3],
    'author': row[4],
    'stock': row[5]
  }

  return render_template('edit.html', book=book)

### updateアクション
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
  title = request.form['title']
  price = request.form['price']
  arrival_day = request.form['arrival_day']
  author = request.form['author']
  stock = request.form['stock']

  con = sqlite3.connect(DATABASE)
  con.execute('''
    UPDATE books 
    SET title = ?, price = ?, arrival_day = ?, author = ?, stock = ?
    WHERE id = ?
  ''', (title, price, arrival_day, author, stock, id))
  con.commit()
  con.close()

  return redirect(url_for('show', id=id))

### deleteアクション
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
  deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  con = sqlite3.connect(DATABASE)
  con.execute('UPDATE books SET deleted_at = ? WHERE id = ?', (deleted_at, id))
  con.commit()
  con.close()

  return redirect(url_for('index'))

### --- 注文に関するアクション ---

### orderアクション
@app.route('/order/<int:id>')
def order(id):
  con = sqlite3.connect(DATABASE)
  row = con.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
  con.close()

  if row is None:
      return '本が見つかりませんでした', 404

  book = {
    'id': row[0],
    'title': row[1],
    'price': row[2],
    'stock': row[5]
  }
  return render_template('order.html', book=book)

### order_confirmアクション
@app.route('/order/confirm/<int:id>', methods=['POST'])
def confirm(id):
  volume = int(request.form['volume'])

  con = sqlite3.connect(DATABASE)
  book_row = con.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
  con.close()

  if book_row is None:
    return '本が見つかりませんでした', 404

  book = {
    'id': book_row[0],
    'title': book_row[1],
    'price': book_row[2],
    'stock': book_row[5]
  }

  # 注文数が在庫数を超えていないかチェック
  if volume > book['stock']:
    return render_template('order_error.html', book=book)

  total_price = book['price'] * volume

  return render_template('confirm.html', book=book, volume=volume, total_price=total_price)

### order_completeアクション
@app.route('/order/complete', methods=['POST'])
def complete():
  book_id = request.form['book_id']
  volume = request.form['volume']
  total_price = request.form['total_price']
  ordered_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  # 在庫数を減らす
  con = sqlite3.connect(DATABASE)
  con.execute('''
    UPDATE books
    SET stock = stock - ?
    WHERE id = ?
  ''', (volume, book_id))

  # 注文を保存
  con.execute('''
    INSERT INTO orders (book_id, volume, total_price, ordered_at)
    VALUES (?, ?, ?, ?)''',
    (book_id, volume, total_price, ordered_at))
  con.commit()
  con.close()

  return render_template('complete.html')