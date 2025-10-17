import sqlite3
import os

def main():
    db_file = "online_cinema.db"
    
    # Удаляем базу, если есть
    if os.path.exists(db_file):
        os.remove(db_file)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Genres (
        GenreID INTEGER PRIMARY KEY,
        GenreName TEXT NOT NULL
    );

    CREATE TABLE Movies (
        MovieID INTEGER PRIMARY KEY,
        Title TEXT NOT NULL,
        Year INTEGER,
        GenreID INTEGER,
        FOREIGN KEY (GenreID) REFERENCES Genres(GenreID)
    );

    CREATE TABLE Halls (
        HallID INTEGER PRIMARY KEY,
        HallName TEXT NOT NULL,
        Capacity INTEGER
    );

    CREATE TABLE Sessions (
        SessionID INTEGER PRIMARY KEY,
        MovieID INTEGER,
        HallID INTEGER,
        SessionDate TEXT,  -- ISO format datetime string
        TicketPrice REAL,
        FOREIGN KEY (MovieID) REFERENCES Movies(MovieID),
        FOREIGN KEY (HallID) REFERENCES Halls(HallID)
    );

    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        City TEXT
    );

    CREATE TABLE Tickets (
        TicketID INTEGER PRIMARY KEY,
        SessionID INTEGER,
        CustomerID INTEGER,
        SeatNumber TEXT,
        FOREIGN KEY (SessionID) REFERENCES Sessions(SessionID),
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
    );
    """)

    # Вставляем данные

    genres = [
        (1, "Драма"),
        (2, "Комедия"),
        (3, "Боевик")
    ]

    movies = [
        (1, "Фильм А", 2022, 1),
        (2, "Фильм Б", 2023, 2),
        (3, "Фильм В", 2024, 3)
    ]

    halls = [
        (1, "Зал 1", 100),
        (2, "Зал 2", 80)
    ]

    sessions = [
        (1, 1, 1, "2025-10-20 18:00:00", 300.0),
        (2, 2, 1, "2025-10-20 20:00:00", 250.0),
        (3, 3, 2, "2025-10-21 19:00:00", 350.0),
        (4, 1, 2, "2025-10-22 18:30:00", 320.0),
    ]

    customers = [
        (1, "Иван", "Иванов", "Москва"),
        (2, "Мария", "Петрова", "Санкт-Петербург"),
        (3, "Алексей", "Смирнов", "Казань")
    ]

    tickets = [
        # Иван Иванов купил 2 билета на разные сеансы (1 и 3)
        (1, 1, 1, "A1"),
        (2, 3, 1, "B3"),

        # Мария Петрова — 1 билет только
        (3, 2, 2, "A5"),

        # Алексей Смирнов — 2 билета, но оба на один сеанс (4)
        (4, 4, 3, "C7"),
        (5, 4, 3, "C8"),
    ]

    cursor.executemany("INSERT INTO Genres VALUES (?, ?);", genres)
    cursor.executemany("INSERT INTO Movies VALUES (?, ?, ?, ?);", movies)
    cursor.executemany("INSERT INTO Halls VALUES (?, ?, ?);", halls)
    cursor.executemany("INSERT INTO Sessions VALUES (?, ?, ?, ?, ?);", sessions)
    cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?);", customers)
    cursor.executemany("INSERT INTO Tickets VALUES (?, ?, ?, ?);", tickets)
    conn.commit()

    # SQL запрос — выводим информацию о клиентах, купивших билеты на минимум 2 разных сеанса
    cursor.execute("""
    SELECT 
        m.Title,
        g.GenreName,
        s.SessionDate,
        c.FirstName,
        c.LastName,
        c.City,
        s.TicketPrice
    FROM Tickets t
    JOIN Sessions s ON t.SessionID = s.SessionID
    JOIN Movies m ON s.MovieID = m.MovieID
    JOIN Genres g ON m.GenreID = g.GenreID
    JOIN Customers c ON t.CustomerID = c.CustomerID
    WHERE t.CustomerID IN (
        SELECT CustomerID
        FROM Tickets
        GROUP BY CustomerID
        HAVING COUNT(DISTINCT SessionID) >= 2
    )
    ORDER BY s.SessionDate;
    """)

    rows = cursor.fetchall()

    print("Клиенты, купившие не менее 2 билетов на разные сеансы:")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
