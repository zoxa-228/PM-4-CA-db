import sqlite3
import os

def main():
    db_file = "students_courses.db"

    # Если файл базы уже есть — удаляем его (чтобы стартовать с чистого листа)
    if os.path.exists(db_file):
        os.remove(db_file)

    # Подключаемся — файл создастся, если его нет
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Создаем таблицы
    cursor.executescript("""
    CREATE TABLE Students (
        StudentID INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL
    );

    CREATE TABLE Courses (
        CourseID INTEGER PRIMARY KEY,
        CourseName TEXT NOT NULL
    );

    CREATE TABLE Enrollments (
        EnrollmentID INTEGER PRIMARY KEY,
        StudentID INTEGER,
        CourseID INTEGER,
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
        FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
    );
    """)

    # Заполняем таблицы данными
    students = [
        (1, "Иван", "Иванов"),
        (2, "Мария", "Петрова"),
        (3, "Игорь", "Исаев"),
        (4, "Алексей", "Смирнов"),
        (5, "Ирина", "Ильина"),
    ]

    courses = [
        (1, "Математика"),
        (2, "Физика"),
        (3, "Информатика")
    ]

    enrollments = [
        (1, 1, 1),  # Иван Иванов - Математика
        (2, 1, 3),  # Иван Иванов - Информатика
        (3, 2, 2),  # Мария Петрова - Физика
        (4, 3, 3),  # Игорь Исаев - Информатика
        (5, 4, 1),  # Алексей Смирнов - Математика
        (6, 5, 2),  # Ирина Ильина - Физика
        (7, 5, 3)   # Ирина Ильина - Информатика
    ]

    cursor.executemany("INSERT INTO Students VALUES (?, ?, ?);", students)
    cursor.executemany("INSERT INTO Courses VALUES (?, ?);", courses)
    cursor.executemany("INSERT INTO Enrollments VALUES (?, ?, ?);", enrollments)
    conn.commit()

    # Запрос с INNER JOIN и фильтром по фамилии на "И"
    cursor.execute("""
    SELECT s.StudentID, s.FirstName, s.LastName, c.CourseName
    FROM Students s
    INNER JOIN Enrollments e ON s.StudentID = e.StudentID
    INNER JOIN Courses c ON e.CourseID = c.CourseID
    WHERE s.LastName LIKE 'И%'
    ORDER BY s.StudentID;
    """)

    rows = cursor.fetchall()
    print("Студенты с фамилией на 'И' и их курсы:")
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
