from flask import Flask
app = Flask(__name__)
import flaskr.main

from flaskr import db
db.create_books_table()
db.create_orders_table()