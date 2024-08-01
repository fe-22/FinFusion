import os
import pymysql
import pandas as pd

# Configuring database connection
host = os.getenv('127.0.0.1')
port = os.getenv('3306')
user = os.getenv('root')
password = os.getenv('')
database = os.getenv('fintech')

conn = pymysql.connect(
    host=host,
    port=int(3306),
    user="root",
    passwd=password,
    db='fintech',
    charset='utf8mb4'
)
cursor = conn.cursor()

class Transaction:
    def __init__(self, id, value, comment, method, type, subtype, date):
        self.id = id
        self.value = value
        self.comment = comment
        self.method = method
        self.type = type
        self.subtype = subtype
        self.date = date
        
class FinancialController:
    def __init__(self, conn):
        self.conn = conn

    def add_transaction(self, transaction):
        # Insert transaction into database
        cursor = self.conn.cursor()
        query = "INSERT INTO transactions (value, comment, method, type, subtype, date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (transaction.value, transaction.comment, transaction.method, transaction.type, transaction.subtype, transaction.date))
        self.conn.commit()

    def get_transactions(self):
        # Retrieve transactions from database
        cursor = self.conn.cursor()
        query = "SELECT * FROM transactions"
        cursor.execute(query)
        transactions = cursor.fetchall()
        return transactions