import sqlite3
import bcrypt
from cryptography.fernet import Fernet

# === Генерация или загрузка ключа шифрования ===
# ⚠️ В реальном проекте этот ключ нужно хранить в .env или конфиге
key = Fernet.generate_key()
cipher = Fernet(key)

# === Подключение к базе данных ===
conn = sqlite3.connect('social_network.db')
cursor = conn.cursor()

# === Создание таблиц ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    is_group BOOLEAN
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_members (
    chat_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY(chat_id, user_id),
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    sender_id INTEGER,
    encrypted_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chat_id) REFERENCES chats(id),
    FOREIGN KEY(sender_id) REFERENCES users(id)
)
''')

conn.commit()

# === Функции ===

def register_user(username, password):
    password = password[:72]  # ограничиваем длину пароля для bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"✅ Пользователь {username} зарегистрирован.")
    except sqlite3.IntegrityError:
        print(f"⚠️ Имя пользователя {username} уже занято.")


def authenticate_user(username, password):
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        print("🔓 Аутентификация успешна.")
        return True
    print("❌ Неверный логин или пароль.")
    return False


def create_post(user_id, content):
    cursor.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content))
    conn.commit()


def add_comment(post_id, user_id, content):
    cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)", (post_id, user_id, content))
    conn.commit()


def create_chat(name, is_group):
    cursor.execute("INSERT INTO chats (name, is_group) VALUES (?, ?)", (name, is_group))
    conn.commit()
    return cursor.lastrowid


def add_member_to_chat(chat_id, user_id):
    cursor.execute("INSERT OR IGNORE INTO chat_members (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
    conn.commit()


def send_message(chat_id, sender_id, message):
    encrypted_message = cipher.encrypt(message.encode('utf-8'))
    cursor.execute(
        "INSERT INTO messages (chat_id, sender_id, encrypted_message) VALUES (?, ?, ?)",
        (chat_id, sender_id, encrypted_message.decode('utf-8'))
    )
    conn.commit()


def read_messages(chat_id):
    cursor.execute("SELECT sender_id, encrypted_message, created_at FROM messages WHERE chat_id = ? ORDER BY created_at", (chat_id,))
    messages = cursor.fetchall()
    for sender_id, encrypted_msg, created_at in messages:
        decrypted_msg = cipher.decrypt(encrypted_msg.encode('utf-8')).decode('utf-8')
        print(f"[{created_at}] User {sender_id}: {decrypted_msg}")


def get_user_id(username):
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


# === Тестовый сценарий ===
if __name__ == "__main__":
    # Регистрация пользователей
    register_user("Alice", "password123")
    register_user("Bob", "securepass")
    register_user("Alex", "alpha123")
    register_user("Max", "maxpower")
    register_user("Liza", "lizapass")
    register_user("Mark", "markcool")

    # Посты и комментарии
    create_post(1, "Привет, это мой первый пост!")
    add_comment(1, 2, "Отличный пост, Alice!")
    create_post(3, "Сегодня солнечно, настроение супер ☀️")
    add_comment(2, 3, "Согласен, день отличный!")

    # Чат Alice и Bob
    chat1 = create_chat("Alice & Bob", False)
    add_member_to_chat(chat1, 1)
    add_member_to_chat(chat1, 2)
    send_message(chat1, 1, "Привет, Bob!")
    send_message(chat1, 2, "Привет, Alice! Как дела?")
    print("\n💬 Сообщения в чате Alice & Bob:")
    read_messages(chat1)

    # Чат Alex и Max
    alex_id = get_user_id("Alex")
    max_id = get_user_id("Max")
    chat2 = create_chat("Alex & Max", False)
    add_member_to_chat(chat2, alex_id)
    add_member_to_chat(chat2, max_id)
    send_message(chat2, alex_id, "Привет, Макс! Готов к проекту?")
    send_message(chat2, max_id, "Да, уже все настроил!")
    print("\n💬 Сообщения в чате Alex & Max:")
    read_messages(chat2)

    # Групповой чат (Liza, Mark, Alice)
    group_chat = create_chat("Команда проекта", True)
    add_member_to_chat(group_chat, get_user_id("Liza"))
    add_member_to_chat(group_chat, get_user_id("Mark"))
    add_member_to_chat(group_chat, get_user_id("Alice"))
    send_message(group_chat, get_user_id("Liza"), "Ребята, дедлайн завтра!")
    send_message(group_chat, get_user_id("Mark"), "Я уже всё сдал 😎")
    send_message(group_chat, get_user_id("Alice"), "Класс! Я почти закончила.")
    print("\n💬 Групповой чат 'Команда проекта':")
    read_messages(group_chat)

    conn.close()
