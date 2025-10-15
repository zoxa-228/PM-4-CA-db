import sqlite3
import os
from datetime import date

# SQL-скрипт для создания таблиц с ключами и связями
CREATE_TABLES_SQL = """
-- Таблица Авторов (Authors)
CREATE TABLE Authors (
    author_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_year INTEGER
);

-- Таблица Жанров (Genres)
CREATE TABLE Genres (
    genre_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Таблица Пользователей (Users)
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    registration_date DATE NOT NULL
);

-- Таблица Книг (Books)
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    publish_year INTEGER,
    author_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES Authors(author_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE RESTRICT
);

-- Таблица Отзывов (Reviews)
CREATE TABLE Reviews (
    review_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
    UNIQUE (user_id, book_id) -- Ограничение: один пользователь - один отзыв на книгу
);
"""

DATABASE_NAME = 'online_library.db'

def create_database(db_name, sql_script):
    """Создает базу данных и таблицы, используя предоставленный SQL-скрипт."""
    try:
        # Устанавливаем соединение с базой данных (файл будет создан, если не существует)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Включаем поддержку внешних ключей в SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Выполняем скрипт создания таблиц
        cursor.executescript(sql_script)

        conn.commit()
        print(f"База данных '{db_name}' и все таблицы успешно созданы.")

        return conn

    except sqlite3.Error as e:
        print(f"Произошла ошибка SQLite: {e}")
        return None
    finally:
        # Соединение будет закрыто в функции main, если оно было успешно установлено
        pass

def populate_sample_data(conn):
    """Заполняет таблицы небольшим количеством демонстрационных данных."""
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # 1. Авторы
        cursor.execute("INSERT INTO Authors (full_name, birth_year) VALUES ('Фёдор Достоевский', 1821);")
        cursor.execute("INSERT INTO Authors (full_name, birth_year) VALUES ('Джордж Оруэлл', 1903);")
        
        # 2. Жанры
        cursor.execute("INSERT INTO Genres (name) VALUES ('Классика');")
        cursor.execute("INSERT INTO Genres (name) VALUES ('Фантастика');")

        # 3. Пользователи
        current_date = date.today().isoformat()
        cursor.execute("INSERT INTO Users (name, email, password, registration_date) VALUES (?, ?, ?, ?);", 
                       ('Алиса Смирнова', 'alice@example.com', 'hashed_pass1', current_date))
        cursor.execute("INSERT INTO Users (name, email, password, registration_date) VALUES (?, ?, ?, ?);", 
                       ('Борис Иванов', 'boris@example.com', 'hashed_pass2', current_date))

        # 4. Книги (author_id 1=Достоевский, genre_id 1=Классика; author_id 2=Оруэлл, genre_id 2=Фантастика)
        cursor.execute("INSERT INTO Books (title, publish_year, author_id, genre_id) VALUES (?, ?, ?, ?);", 
                       ('Преступление и наказание', 1866, 1, 1))
        cursor.execute("INSERT INTO Books (title, publish_year, author_id, genre_id) VALUES (?, ?, ?, ?);", 
                       ('1984', 1949, 2, 2))

        # 5. Отзывы (user_id 1=Алиса, book_id 2=1984; user_id 2=Борис, book_id 1=Преступление)
        review_date = date.today().isoformat()
        cursor.execute("INSERT INTO Reviews (user_id, book_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?);",
                       (1, 2, 5, 'Шедевр антиутопии, очень актуально!', review_date))
        cursor.execute("INSERT INTO Reviews (user_id, book_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?);",
                       (2, 1, 4, 'Глубокое, но тяжелое произведение.', review_date))

        conn.commit()
        print("Демонстрационные данные успешно добавлены.")
        
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении данных: {e}")
        conn.rollback()


def main():
    # Удаляем старый файл, если он существует, для чистого запуска
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
        print(f"Существующий файл базы данных '{DATABASE_NAME}' удален.")

    # Создаем базу данных и таблицы
    conn = create_database(DATABASE_NAME, CREATE_TABLES_SQL)

    if conn:
        # Добавляем примеры данных
        populate_sample_data(conn)

        # Выполняем тестовый запрос для проверки связей
        print("\n--- Проверка данных (Книга и её Отзыв) ---")
        cursor = conn.cursor()
        query = """
        SELECT 
            B.title, 
            U.name AS user_name, 
            R.rating, 
            R.comment
        FROM Books B
        JOIN Reviews R ON B.book_id = R.book_id
        JOIN Users U ON R.user_id = U.user_id
        WHERE B.title = '1984';
        """
        
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            print(f"Название книги: {results[0][0]}")
            for row in results:
                print(f"  > Отзыв от: {row[1]}, Оценка: {row[2]}/5, Комментарий: '{row[3]}'")
        else:
            print("Отзывы не найдены.")

        # Закрываем соединение
        conn.close()
        print("\nСоединение с базой данных закрыто.")

if __name__ == "__main__":
    main()