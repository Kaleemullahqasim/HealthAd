import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 email TEXT PRIMARY KEY,
                 password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT,
                 origin TEXT,
                 message TEXT,
                 FOREIGN KEY (email) REFERENCES users(email))''')
    conn.commit()
    conn.close()

def add_user(email, password):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    hashed_password = generate_password_hash(password)
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
    conn.commit()
    conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

def get_chat_history(email):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("SELECT origin, message FROM history WHERE email=?", (email,))
    history = c.fetchall()
    conn.close()
    return [{"origin": row[0], "message": row[1]} for row in history]

def add_chat_message(email, origin, message):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (email, origin, message) VALUES (?, ?, ?)",
              (email, origin, message))
    conn.commit()
    conn.close()
