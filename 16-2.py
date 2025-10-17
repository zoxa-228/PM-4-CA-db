import sqlite3
import os

def main():
    db_file = "16-2.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Courses (
        course_id INTEGER PRIMARY KEY,
        course_title TEXT NOT NULL
    );

    CREATE TABLE Enrollments (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        enrollment_date TEXT,
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    );
    """)

    # Вставляем данные в Courses
    courses = [
        (1, "Математика"),
        (2, "Физика"),
        (3, "История"),
        (4, "Программирование"),
    ]
    cursor.executemany("INSERT INTO Courses VALUES (?, ?);", courses)

    # Вставляем данные в Enrollments (записан только на курсы 1 и 4)
    enrollments = [
        (1, 101, 1, "2025-01-15"),
        (2, 102, 4, "2025-02-10"),
        (3, 103, 1, "2025-03-05"),
    ]
    cursor.executemany("INSERT INTO Enrollments VALUES (?, ?, ?, ?);", enrollments)
    conn.commit()

    # Запрос курсов без регистраций
    cursor.execute("""
    SELECT c.course_id, c.course_title
    FROM Courses c
    LEFT JOIN Enrollments e ON c.course_id = e.course_id
    WHERE e.enrollment_id IS NULL;
    """)

    print("Курсы без зарегистрированных студентов:")
    for row in cursor.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
