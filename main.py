import telebot
import random
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("YOUR_TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 1238343405

USER_DATA_FILE = "users.txt"
ASSIGNMENTS_FILE = "assignments.txt"

def save_user_data(user_id, name, wish):
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{user_id}|{name}|{wish}\n")

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return []
    with open(USER_DATA_FILE, "r") as f:
        return [line.strip().split("|") for line in f.readlines()]

def save_assignments(assignments):
    with open(ASSIGNMENTS_FILE, "w") as f:
        for giver_id, receiver_id, receiver_name, receiver_wish in assignments:
            f.write(f"{giver_id}|{receiver_id}|{receiver_name}|{receiver_wish}\n")

def load_assignments():
    if not os.path.exists(ASSIGNMENTS_FILE):
        return []
    with open(ASSIGNMENTS_FILE, "r") as f:
        return [line.strip().split("|") for line in f.readlines()]

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

if __name__ == "__main__":
    print('Бот запушен')
    bot.polling(none_stop=True)
