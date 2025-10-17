import sqlite3
from datetime import datetime

# Подключение к БД
conn = sqlite3.connect("online_store.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# === Создание таблиц ===

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
""")

# === Вставка данных ===

# Customers
cursor.executemany("""
INSERT INTO Customers (name, email)
VALUES (?, ?);
""", [
    ("Алиса", "alice@example.com"),
    ("Боб", "bob@example.com"),
    ("Клара", "clara@example.com")
])

# Categories
cursor.executemany("""
INSERT INTO Categories (name)
VALUES (?);
""", [
    ("Электроника",),
    ("Одежда",),
    ("Книги",)
])

# Products
cursor.executemany("""
INSERT INTO Products (name, price, category_id)
VALUES (?, ?, ?);
""", [
    ("Смартфон", 500.00, 1),
    ("Наушники", 100.00, 1),
    ("Футболка", 20.00, 2),
    ("Джинсы", 40.00, 2),
    ("Роман", 15.00, 3),
    ("Энциклопедия", 60.00, 3)
])

# Orders
cursor.executemany("""
INSERT INTO Orders (customer_id, order_date)
VALUES (?, ?);
""", [
    (1, "2023-02-01"),
    (2, "2022-12-15"),
    (1, "2023-10-01"),
    (3, "2023-07-10")
])

# OrderItems
cursor.executemany("""
INSERT INTO OrderItems (order_id, product_id, quantity)
VALUES (?, ?, ?);
""", [
    (1, 1, 1),  # Алиса купила смартфон
    (1, 2, 2),  # и наушники
    (2, 3, 1),  # Боб купил футболку
    (3, 6, 1),  # Алиса купила энциклопедию
    (3, 5, 2),  # и 2 романа
    (4, 4, 1),  # Клара купила джинсы
    (4, 1, 1),  # и смартфон
])

conn.commit()

# === Запросы ===

print("\n1. Клиенты, сделавшие заказы после 2023-01-01:")
cursor.execute("""
SELECT DISTINCT c.name, c.email
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
WHERE o.order_date > '2023-01-01';
""")
for row in cursor.fetchall():
    print(row)

print("\n2. Количество проданных товаров по категориям:")
cursor.execute("""
SELECT cat.name, SUM(oi.quantity) as total_sold
FROM OrderItems oi
JOIN Products p ON oi.product_id = p.product_id
JOIN Categories cat ON p.category_id = cat.category_id
GROUP BY cat.category_id;
""")
for row in cursor.fetchall():
    print(row)

print("\n3. Топ-3 самых дорогих товаров:")
cursor.execute("""
SELECT name, price
FROM Products
ORDER BY price DESC
LIMIT 3;
""")
for row in cursor.fetchall():
    print(row)

print("\n4. Список заказов с общей суммой (price * quantity):")
cursor.execute("""
SELECT o.order_id, c.name, SUM(p.price * oi.quantity) as total_amount
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
JOIN OrderItems oi ON o.order_id = oi.order_id
JOIN Products p ON oi.product_id = p.product_id
GROUP BY o.order_id;
""")
for row in cursor.fetchall():
    print(row)

print("\n5. Клиент, потративший больше всего денег:")
cursor.execute("""
SELECT c.name, SUM(p.price * oi.quantity) as total_spent
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
JOIN OrderItems oi ON o.order_id = oi.order_id
JOIN Products p ON oi.product_id = p.product_id
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 1;
""")
print(cursor.fetchone())

# === Завершение ===
conn.close()
