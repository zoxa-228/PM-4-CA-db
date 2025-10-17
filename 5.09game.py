import sqlite3

# Подключаемся к базе (создаётся файл game_platform.db)
conn = sqlite3.connect("game_platform.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Создаём таблицы
cursor.executescript("""
DROP TABLE IF EXISTS PlayerScores;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS Games;

CREATE TABLE Players (
    PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    RegistrationDate TEXT NOT NULL
);

CREATE TABLE Games (
    GameID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL
);

CREATE TABLE Matches (
    MatchID INTEGER PRIMARY KEY AUTOINCREMENT,
    GameID INTEGER NOT NULL,
    MatchDate TEXT NOT NULL,
    FOREIGN KEY (GameID) REFERENCES Games(GameID)
);

CREATE TABLE PlayerScores (
    PlayerScoreID INTEGER PRIMARY KEY AUTOINCREMENT,
    MatchID INTEGER NOT NULL,
    PlayerID INTEGER NOT NULL,
    Score INTEGER NOT NULL,
    Kills INTEGER NOT NULL,
    Deaths INTEGER NOT NULL,
    Won BOOLEAN NOT NULL,
    FOREIGN KEY (MatchID) REFERENCES Matches(MatchID),
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID)
);
""")

# Вставляем игроков (5)
players = [
    ("Alice", "2024-01-10"),
    ("Bob", "2023-11-15"),
    ("Charlie", "2024-05-20"),
    ("Diana", "2024-03-05"),
    ("Evan", "2023-09-30")
]
cursor.executemany("INSERT INTO Players (Name, RegistrationDate) VALUES (?, ?);", players)

# Вставляем игры (3)
games = [
    ("Cyber Arena",),
    ("Space Battle",),
    ("Mystic Quest",)
]
cursor.executemany("INSERT INTO Games (Title) VALUES (?);", games)

# Вставляем матчи (9), связываем с играми
matches = [
    (1, "2024-04-01"),
    (1, "2024-04-05"),
    (2, "2024-03-15"),
    (2, "2024-03-20"),
    (3, "2024-02-10"),
    (3, "2024-02-15"),
    (1, "2024-04-10"),
    (2, "2024-03-25"),
    (3, "2024-02-20"),
]
cursor.executemany("INSERT INTO Matches (GameID, MatchDate) VALUES (?, ?);", matches)

# Вставляем результаты игроков в матчах (PlayerScores)
player_scores = [
    # Match 1 (Cyber Arena)
    (1, 1, 1500, 10, 5, True),   # Alice won
    (1, 2, 1200, 8, 7, False),   # Bob
    (1, 3, 1300, 9, 6, False),   # Charlie

    # Match 2 (Cyber Arena)
    (2, 2, 1400, 12, 4, True),   # Bob won
    (2, 4, 1100, 7, 8, False),   # Diana
    (2, 5, 900, 5, 9, False),    # Evan

    # Match 3 (Space Battle)
    (3, 1, 1600, 15, 3, True),   # Alice won
    (3, 3, 1000, 6, 10, False),  # Charlie

    # Match 4 (Space Battle)
    (4, 2, 1300, 11, 5, True),   # Bob won
    (4, 4, 1200, 10, 6, False),  # Diana

    # Match 5 (Mystic Quest)
    (5, 3, 1100, 8, 7, True),    # Charlie won
    (5, 5, 1050, 7, 8, False),   # Evan

    # Match 6 (Mystic Quest)
    (6, 1, 1400, 12, 4, True),   # Alice won
    (6, 4, 1000, 5, 9, False),   # Diana

    # Match 7 (Cyber Arena)
    (7, 3, 1350, 11, 6, True),   # Charlie won
    (7, 5, 900, 5, 12, False),   # Evan

    # Match 8 (Space Battle)
    (8, 2, 1250, 10, 7, True),   # Bob won
    (8, 1, 1150, 9, 8, False),   # Alice

    # Match 9 (Mystic Quest)
    (9, 4, 1300, 12, 3, True),   # Diana won
    (9, 5, 1100, 8, 7, False),   # Evan
]
cursor.executemany("""
INSERT INTO PlayerScores (MatchID, PlayerID, Score, Kills, Deaths, Won)
VALUES (?, ?, ?, ?, ?, ?);
""", player_scores)

conn.commit()

print("=== Задание 1: Игроки, зарегистрировавшиеся в 2024 году ===")
cursor.execute("""
SELECT PlayerID, Name, RegistrationDate
FROM Players
WHERE RegistrationDate LIKE '2024%';
""")
for row in cursor.fetchall():
    print(row)

print("\n=== Задание 2: Средний балл игрока с PlayerID=1 ===")
cursor.execute("""
SELECT AVG(Score) FROM PlayerScores WHERE PlayerID = 1;
""")
print(cursor.fetchone()[0])

print("\n=== Задание 3: 5 самых популярных игр по количеству матчей ===")
cursor.execute("""
SELECT g.Title, COUNT(m.MatchID) as MatchCount
FROM Games g
JOIN Matches m ON g.GameID = m.GameID
GROUP BY g.GameID
ORDER BY MatchCount DESC
LIMIT 5;
""")
for row in cursor.fetchall():
    print(row)

print("\n=== Задание 4: Игрок с самым высоким средним K/D ===")
cursor.execute("""
SELECT p.PlayerID, p.Name, AVG(CAST(ps.Kills AS FLOAT)/NULLIF(ps.Deaths,0)) as Avg_KD
FROM Players p
JOIN PlayerScores ps ON p.PlayerID = ps.PlayerID
GROUP BY p.PlayerID
ORDER BY Avg_KD DESC
LIMIT 1;
""")
print(cursor.fetchone())

print("\n=== Задание 5: Игроки, которые играли в 'Cyber Arena', но не выиграли ни одного матча ===")
cursor.execute("""
SELECT DISTINCT p.PlayerID, p.Name
FROM Players p
JOIN PlayerScores ps ON p.PlayerID = ps.PlayerID
JOIN Matches m ON ps.MatchID = m.MatchID
JOIN Games g ON m.GameID = g.GameID
WHERE g.Title = 'Cyber Arena'
AND p.PlayerID NOT IN (
    SELECT PlayerID FROM PlayerScores ps2
    JOIN Matches m2 ON ps2.MatchID = m2.MatchID
    JOIN Games g2 ON m2.GameID = g2.GameID
    WHERE g2.Title = 'Cyber Arena' AND ps2.Won = 1
);
""")
for row in cursor.fetchall():
    print(row)

print("\n=== Задание 6: Полная статистика матча с MatchID=2 ===")
cursor.execute("""
SELECT 
    m.MatchID, g.Title as GameTitle, p.Name as PlayerName,
    ps.Score, ps.Kills, ps.Deaths,
    CASE WHEN ps.Deaths = 0 THEN CAST(ps.Kills AS FLOAT) ELSE CAST(ps.Kills AS FLOAT)/ps.Deaths END as K_D_Ratio,
    ps.Won
FROM Matches m
JOIN Games g ON m.GameID = g.GameID
JOIN PlayerScores ps ON m.MatchID = ps.MatchID
JOIN Players p ON ps.PlayerID = p.PlayerID
WHERE m.MatchID = 2
ORDER BY p.Name;
""")
for row in cursor.fetchall():
    print(row)

conn.close()
