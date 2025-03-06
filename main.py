# import json
# import requests
# from apscheduler.schedulers.background import BackgroundScheduler
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# import time
#
# from apiary import create_apiary, check_beehive_exists, view_apiary
# from jwt_token import *
# from telebot import types
# from login import process_login
# from registration import process_registration
# from bot_config import bot
#
# SERVER_URL = "https://smart-beehive-server.onrender.com/getdata"
# SERVER_CREATE_APIARY = "https://smart-beehive-server.onrender.com/api/"
#
# last_data = None
# creating_apiary = False  # блокування кнопок під час створення пасіки
#
#
# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     chat_id = message.chat.id
#     markup = types.InlineKeyboardMarkup()
#
#     if get_token(chat_id) is None:
#         markup.add(types.InlineKeyboardButton('Вхід', callback_data='login'))
#         markup.add(types.InlineKeyboardButton(
#             'Реєстрація', callback_data='registration'))
#
#     else:
#         if check_beehive_exists():
#             markup.add(types.InlineKeyboardButton(
#                 'Переглянути пасіку', callback_data='view_apiary'))
#             markup.add(types.InlineKeyboardButton(
#                 'Створити пасіку', callback_data='create_apiary'))
#         else:
#             markup.add(types.InlineKeyboardButton(
#                 'Створити пасіку', callback_data='create_apiary'))
#
#     bot.send_message(chat_id, "Ласкаво просимо!", reply_markup=markup)
#
#
# @bot.callback_query_handler(
#     func=lambda call: call.data in ['login', 'registration', 'create_apiary', 'view_apiary', 'back_in_menu'])
# def callback_handler(call):
#     chat_id = call.message.chat.id
#     message_id = call.message.message_id
#
#     if call.data == 'login':
#         bot.delete_message(chat_id, message_id)
#         process_login(call.message)
#     elif call.data == 'registration':
#         bot.delete_message(chat_id, message_id)
#         process_registration(call.message)
#     elif call.data == 'create_apiary':
#         # todo 5 Добавити заборону натискати кнопки коли вибрано варіант "Створити пасіку"
#         bot.delete_message(chat_id, message_id)
#         create_apiary(call.message)
#     elif call.data == 'view_apiary':
#         bot.delete_message(chat_id, message_id)
#         view_apiary(call.message)
#     elif call.data == 'back_in_menu':
#         bot.delete_message(chat_id, message_id)
#         send_welcome(call.message)
#
#
# if __name__ == "__main__":
#     print("Бот запущено...")
#     bot.polling(none_stop=True)

import os
import json
import requests
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
from apiary import create_apiary, check_beehive_exists, view_apiary
from jwt_token import *
from login import process_login
from registration import process_registration
from bot_config import bot

# Отримуємо токен та URL з змінних середовища
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

SERVER_URL = "https://smart-beehive-server.onrender.com/getdata"
SERVER_CREATE_APIARY = "https://smart-beehive-server.onrender.com/api/"

app = Flask(__name__)

# Головний маршрут для обробки запитів від Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Встановлення вебхука
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    success = bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    if success:
        return "Webhook встановлено!", 200
    else:
        return "Помилка при встановленні вебхука", 400

# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()

    if get_token(chat_id) is None:
        markup.add(types.InlineKeyboardButton('Вхід', callback_data='login'))
        markup.add(types.InlineKeyboardButton('Реєстрація', callback_data='registration'))
    else:
        if check_beehive_exists():
            markup.add(types.InlineKeyboardButton('Переглянути пасіку', callback_data='view_apiary'))
            markup.add(types.InlineKeyboardButton('Створити пасіку', callback_data='create_apiary'))
        else:
            markup.add(types.InlineKeyboardButton('Створити пасіку', callback_data='create_apiary'))

    bot.send_message(chat_id, "Ласкаво просимо!", reply_markup=markup)

# Обробка callback-кнопок
@bot.callback_query_handler(func=lambda call: call.data in ['login', 'registration', 'create_apiary', 'view_apiary', 'back_in_menu'])
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    bot.delete_message(chat_id, message_id)

    if call.data == 'login':
        process_login(call.message)
    elif call.data == 'registration':
        process_registration(call.message)
    elif call.data == 'create_apiary':
        create_apiary(call.message)
    elif call.data == 'view_apiary':
        view_apiary(call.message)
    elif call.data == 'back_in_menu':
        send_welcome(call.message)

if __name__ == "__main__":
    print("Запуск Flask-сервера...")
    app.run(host="0.0.0.0", port=10000)
