from flaskr import app
from flask import render_template, request, redirect, url_for
import sqlite3
DATABASE = 'database.db'

### indexアクション
@app.route('/')
def index():
    con = sqlite3.connect(DATABASE)
    db_books = con.execute('SELECT * FROM books').fetchall()
    con.close()

    books = []
    for row in db_books:
      books.append({'title': row[0], 'price': row[1], 'arrival_day': row[2], 'author': row[3]})
    return render_template(
        'index.html',
        books=books
    )

### formアクション
@app.route('/form')
def form():
  return render_template(
        'form.html'
    )

### registerアクション
@app.route('/register', methods=['POST'])
def register():
  title = request.form['title']
  price = request.form['price']
  arrival_day = request.form['arrival_day']
  author = request.form['author']

  con = sqlite3.connect(DATABASE)
  con.execute('INSERT INTO books VALUES(?, ?, ?, ?)',
              [title, price, arrival_day, author])
  con.commit()
  con.close()

  return redirect(url_for('index'))
