import telebot
import random
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 1238343405

DB_FILE = "data.db"

def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        wish TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS assignments (
        giver_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        receiver_name TEXT NOT NULL,
        receiver_wish TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def save_user_data(user_id, name, wish):
    """Сохраняет данные пользователя в базу данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO users (user_id, name, wish) VALUES (?, ?, ?)', (user_id, name, wish))
    conn.commit()
    conn.close()

def load_user_data():
    """Загружает данные всех пользователей из базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, wish FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def save_assignments(assignments):
    """Сохраняет распределения подарков в базу данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM assignments')  # Очистка предыдущих записей
    cursor.executemany('INSERT INTO assignments (giver_id, receiver_id, receiver_name, receiver_wish) VALUES (?, ?, ?, ?)', assignments)
    conn.commit()
    conn.close()

def load_assignments():
    """Загружает распределения подарков из базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT giver_id, receiver_id, receiver_name, receiver_wish FROM assignments')
    assignments = cursor.fetchall()
    conn.close()
    return assignments

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши своё имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    name = message.text.strip()
    bot.send_message(message.chat.id, "Что ты хочешь получить в подарок?")
    bot.register_next_step_handler(message, get_wish, name)

def get_wish(message, name):
    wish = message.text.strip()
    save_user_data(message.chat.id, name, wish)
    bot.send_message(message.chat.id, "Отлично! Ждите, пока админ распределит участников.")

@bot.message_handler(commands=['distribute'])
def distribute(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    user_data = load_user_data()

    if len(user_data) < 2:
        bot.send_message(message.chat.id, "Недостаточно участников для распределения.")
        return

    random.shuffle(user_data)
    assignments = []
    for i, giver in enumerate(user_data):
        giver_id = giver[0]
        receiver = user_data[(i + 1) % len(user_data)]
        receiver_id, receiver_name, receiver_wish = receiver
        assignments.append((giver_id, receiver_id, receiver_name, receiver_wish))

    save_assignments(assignments)

    for giver_id, _, receiver_name, receiver_wish in assignments:
        try:
            bot.send_message(
                giver_id,
                f"Вы дарите подарок для: {receiver_name}. Его/её пожелание: {receiver_wish}"
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения {giver_id}: {e}")

    bot.send_message(message.chat.id, "Распределение завершено! Сообщения отправлены.")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    user_data = load_user_data()

    if not user_data:
        bot.send_message(message.chat.id, "Нет данных о пользователях.")
        return

    response = "Список пользователей:\n"
    for _, name, wish in user_data:
        response += f"Имя: {name}, Пожелание: {wish}\n"

    bot.send_message(message.chat.id, response)

if __name__ == "__main__":
    init_db()
    print('Бот запущен')
    bot.polling(none_stop=True)
