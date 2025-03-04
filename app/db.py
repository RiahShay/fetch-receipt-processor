import sqlite3
# from models import Receipt, Item
import json
import logging

conn = None

db = None

def init_db():
    global conn, db
    conn = sqlite3.connect('retail_receipt.db')
    db = conn.cursor()

    db.execute('''
        CREATE TABLE IF NOT EXISTS retail_receipts (
            id TEXT PRIMARY KEY,
            retailer TEXT,
            purchase_date DATE,
            purchase_time TIME,
            items TEXT,
            total DOUBLE,
            points INTEGER
        )
    ''')
    conn.commit()




def store_receipt(receipt_id: str, points: int, receipt):
    # convert to receipt
    # store to db
    if conn is None:
        init_db()  # Ensure the database is initialized
    
    try:
        with conn:
            receipt_items = json.dumps(receipt["items"])
            sql = "INSERT INTO retail_receipts (id, retailer, purchase_date, purchase_time, items, total, points) VALUES (?, ?, ?, ?, ?, ?, ?)"
            args = (
              receipt_id,
              receipt["retailer"],
              receipt["purchaseDate"],
              receipt["purchaseTime"],
              receipt_items,
              float(receipt["total"]),
              points)
            db.execute(sql, args)
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.exception(e) 

def get_receipt_points(receipt_id: str):
    if conn is None:
        init_db()  # Ensure the database is initialized
    
    try:
        with conn:
            sql = "SELECT points FROM retail_receipts WHERE id=?"
            db.execute(sql, (receipt_id,))
            result = db.fetchone()
            return result
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        logging.exception(e) 