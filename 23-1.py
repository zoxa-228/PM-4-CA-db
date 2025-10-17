import sqlite3
import os

def main():
    db_file = "23-1.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Customers2024 (
        CustomerID INTEGER PRIMARY KEY,
        CustomerName TEXT NOT NULL
    );

    CREATE TABLE Customers2025 (
        CustomerID INTEGER PRIMARY KEY,
        CustomerName TEXT NOT NULL
    );
    """)

    # Вставляем данные
    customers_2024 = [
        (1, "Иван Иванов"),
        (2, "Мария Петрова"),
        (3, "Сергей Сидоров"),
        (4, "Ольга Смирнова")
    ]

    customers_2025 = [
        (3, "Сергей Сидоров"),
        (4, "Ольга Смирнова"),
        (5, "Анна Кузнецова"),
        (6, "Петр Петров")
    ]

    cursor.executemany("INSERT INTO Customers2024 VALUES (?, ?);", customers_2024)
    cursor.executemany("INSERT INTO Customers2025 VALUES (?, ?);", customers_2025)
    conn.commit()

    # Клиенты, которые были в 2024, но нет в 2025
    print("Клиенты, которые были в 2024, но отсутствуют в 2025:")
    cursor.execute("""
    SELECT CustomerID, CustomerName FROM Customers2024
    EXCEPT
    SELECT CustomerID, CustomerName FROM Customers2025;
    """)
    for row in cursor.fetchall():
        print(row)

    # Клиенты, которые появились только в 2025, отсутствуют в 2024
    print("\nКлиенты, которые появились только в 2025, отсутствуют в 2024:")
    cursor.execute("""
    SELECT CustomerID, CustomerName FROM Customers2025
    EXCEPT
    SELECT CustomerID, CustomerName FROM Customers2024;
    """)
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
