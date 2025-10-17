import sqlite3
import os

def main():
    db_file = "18.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        City TEXT NOT NULL,
        Country TEXT NOT NULL
    );

    CREATE TABLE Employees (
        EmployeeID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        City TEXT NOT NULL,
        Country TEXT NOT NULL
    );
    """)

    # Вставляем тестовые данные
    customers = [
        (1, "Anna Schmidt", "Berlin", "Germany"),
        (2, "Pierre Dupont", "Paris", "France"),
        (3, "John Doe", "London", "UK"),
        (4, "Marie Curie", "Lyon", "France")
    ]
    employees = [
        (1, "Max Mustermann", "Munich", "Germany"),
        (2, "Jean Valjean", "Lille", "France"),
        (3, "Alice Johnson", "New York", "USA"),
        (4, "Hans Zimmer", "Berlin", "Germany")
    ]

    cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?);", customers)
    cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?);", employees)
    conn.commit()

    # Выполняем запрос
    cursor.execute("""
    SELECT CustomerID AS PersonID, Name, City, Country, 'Customer' AS Role
    FROM Customers
    WHERE Country IN ('Germany', 'France')

    UNION ALL

    SELECT EmployeeID AS PersonID, Name, City, Country, 'Employee' AS Role
    FROM Employees
    WHERE Country IN ('Germany', 'France')

    ORDER BY City, Name;
    """)

    print("Список всех людей из Германии и Франции с ролью:")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
