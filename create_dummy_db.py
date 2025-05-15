import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()
fake = Faker()

# Drop tables if they exist
cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS orders")

# Create tables
cursor.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)
""")

cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    status TEXT,
    date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# Populate customers
for _ in range(20):
    name = fake.name()
    email = fake.email()
    cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))

# Populate products
products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Tablet", "Headphones"]
for p in products:
    price = round(random.uniform(50, 1500), 2)
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (p, price))

# Populate orders
statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
for _ in range(50):
    customer_id = random.randint(1, 20)
    product_id = random.randint(1, len(products))
    status = random.choice(statuses)
    date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO orders (customer_id, product_id, status, date)
        VALUES (?, ?, ?, ?)""", (customer_id, product_id, status, date))

# Commit and close
conn.commit()
conn.close()
print("Dummy shop.db created.")