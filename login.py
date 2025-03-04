import requests

from jwt_token import save_token
from bot_config import bot

SERVER_LOGIN = "https://smart-beehive-server.onrender.com/api/users/login"

def process_login(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введіть ваш номер телефону:")
    bot.register_next_step_handler(message, ask_password)


def ask_password(message):
    chat_id = message.chat.id
    phone = message.text
    bot.send_message(chat_id, "Введіть ваш пароль:")
    bot.register_next_step_handler(message, check_login, phone)


def check_login(message, phone):
    chat_id = message.chat.id
    password = message.text

    # Відправка запиту на сервер для перевірки користувача
    response = requests.post(f"{SERVER_LOGIN}", json={"phonenumber": phone, "password": password})
    if response.status_code == 200:
        response_data = response.json()
        if response_data:
            save_token(message.chat.id, response.text)
            bot.send_message(chat_id, "Вхід успішний!")
            from main import send_welcome
            send_welcome(message)
        else:
            bot.send_message(chat_id, "Користувача не знайдено.")
    else:
        bot.send_message(chat_id, "Помилка підключення до сервера.")
