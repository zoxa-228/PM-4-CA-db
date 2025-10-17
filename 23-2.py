import sqlite3
import os

def main():
    db_file = "23-2.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE WebUsers (
        UserID INTEGER PRIMARY KEY,
        UserName TEXT NOT NULL
    );

    CREATE TABLE AppUsers (
        UserID INTEGER PRIMARY KEY,
        UserName TEXT NOT NULL
    );
    """)

    # Вставляем данные
    web_users = [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie"),
        (4, "David")
    ]

    app_users = [
        (3, "Charlie"),
        (4, "David"),
        (5, "Eve"),
        (6, "Frank")
    ]

    cursor.executemany("INSERT INTO WebUsers VALUES (?, ?);", web_users)
    cursor.executemany("INSERT INTO AppUsers VALUES (?, ?);", app_users)
    conn.commit()

    # Находим пользователей, которые есть и там, и там
    cursor.execute("""
    SELECT w.UserID, w.UserName
    FROM WebUsers w
    INNER JOIN AppUsers a ON w.UserID = a.UserID;
    """)

    print("Пользователи, которые пользуются и сайтом, и приложением:")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
