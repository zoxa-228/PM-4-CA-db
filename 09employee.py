import sqlite3
import os

def main():
    db_file = "employee_department.db"

    # Если файл БД существует — удаляем, чтобы начать с чистого листа
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Departments (
        DepartmentID INTEGER PRIMARY KEY,
        DepartmentName TEXT NOT NULL,
        ManagerID INTEGER
    );

    CREATE TABLE Employees (
        EmployeeID INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        DepartmentID INTEGER,
        FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
    );
    """)

    # Вставляем данные
    departments = [
        (1, "HR", 101),
        (2, "IT", 102),
        (3, "Finance", 103)
    ]

    employees = [
        (1, "Alice", "Smith", 1),
        (2, "Bob", "Brown", 2),
        (3, "Charlie", "Davis", 5),  # Отдела 5 нет
        (4, "Diana", "Evans", None)  # Отдел не указан
    ]

    cursor.executemany("INSERT INTO Departments VALUES (?, ?, ?);", departments)
    cursor.executemany("INSERT INTO Employees VALUES (?, ?, ?, ?);", employees)
    conn.commit()

    # Выполняем INNER JOIN
    cursor.execute("""
    SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName
    FROM Employees e
    INNER JOIN Departments d ON e.DepartmentID = d.DepartmentID;
    """)

    rows = cursor.fetchall()
    print("Результат INNER JOIN:")
    for r in rows:
        print(r)

    print("""
Объяснение:
INNER JOIN возвращает только тех сотрудников, у которых DepartmentID совпадает с существующим в Departments.
Сотрудники с несуществующим или NULL DepartmentID не попадут в результат.
""")

    conn.close()

if __name__ == "__main__":
    main()
