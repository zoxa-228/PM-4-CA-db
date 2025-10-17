import sqlite3
import os

def main():
    db_file = "18.2.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Customers (
        Name TEXT,
        Phone TEXT
    );

    CREATE TABLE Employees (
        Name TEXT,
        Phone TEXT
    );

    CREATE TABLE Suppliers (
        Name TEXT,
        Phone TEXT
    );
    """)

    # Вставляем данные (с NULL-значениями в Phone)
    customers = [
        ("Иван Иванов", "123456"),
        ("Мария Петрова", None),
        ("Сергей Сидоров", "987654"),
    ]
    employees = [
        ("Алексей Смирнов", "123456"),
        ("Мария Петрова", None),  # Дубликат с NULL
        ("Елена Кузнецова", "555555"),
    ]
    suppliers = [
        ("Петр Петров", None),
        ("Иван Иванов", "123456"),  # Дубликат
        ("Николай Николаев", "777777"),
    ]

    cursor.executemany("INSERT INTO Customers VALUES (?, ?);", customers)
    cursor.executemany("INSERT INTO Employees VALUES (?, ?);", employees)
    cursor.executemany("INSERT INTO Suppliers VALUES (?, ?);", suppliers)
    conn.commit()

    # Запрос объединяющий все три таблицы с заменой NULL и уникальностью
    cursor.execute("""
    SELECT DISTINCT Name, 
        COALESCE(Phone, 'Номер не указан') AS Phone
    FROM (
        SELECT Name, Phone FROM Customers
        UNION ALL
        SELECT Name, Phone FROM Employees
        UNION ALL
        SELECT Name, Phone FROM Suppliers
    );
    """)

    print("Общий список людей с телефонами:")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
