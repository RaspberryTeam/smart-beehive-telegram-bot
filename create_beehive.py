import requests

from apiary import view_apiary
from bot_config import bot
from jwt_token import get_token
from telebot import types

# Створення вулика в пасіку
beehive_data = {}


def request_beehive_name(call):
    chat_id = call.message.chat.id
    if get_token(chat_id) is None:
        bot.send_message(chat_id, "Спочатку авторизуйтеся")
        from main import send_welcome
        send_welcome(call.message)
        return
    msg = bot.send_message(chat_id, "📝 Введіть назву нового вулика:")
    bot.register_next_step_handler(msg, request_beehive_key, call)


def request_beehive_key(message, call):
    chat_id = message.chat.id
    beehive_data[chat_id] = {"name": message.text, "apiary_id": int(call.data.split('_')[2])}
    msg = bot.send_message(chat_id, "🔑 Введіть унікальний ключ для вулика:")
    bot.register_next_step_handler(msg, create_beehive)


def create_beehive(message):
    chat_id = message.chat.id
    from main import send_welcome, SERVER_CREATE_APIARY

    if get_token(chat_id) is None:
        bot.send_message(chat_id, "Спочатку авторизуйтеся")
        send_welcome(chat_id)
        return

    token = get_token(chat_id)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = {
        "beehive_key": message.text,
        "apiaryId": beehive_data[chat_id]["apiary_id"],
        "name": beehive_data[chat_id]["name"]
    }

    try:
        response = requests.post(f"{SERVER_CREATE_APIARY}beehives/", json=data, headers=headers)
        if response.status_code == 201:
            bot.send_message(chat_id, "✅ Вулик успішно створено!")
            view_apiary(message)  # todo 3 Добавити щоб вертало до всіх вуликів
        else:
            bot.send_message(chat_id, "❌ Помилка при створенні вулика")
    except requests.exceptions.RequestException as e:
        print(e)
        bot.send_message(chat_id, "❌ Сталася помилка при з'єднанні з сервером")



