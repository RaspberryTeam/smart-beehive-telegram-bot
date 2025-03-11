import os
import json
from flask import Flask, request
from telebot import types
from bot_config import bot

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    print(f"📩 Отримано запит: {json_str}")  # Додаємо логування у Flask

    update = types.Update.de_json(json_str)
    bot.process_new_updates([update])

    return 'OK', 200


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    
    bot.send_message(chat_id, "Ласкаво просимо!")

    if get_token(chat_id) is None:
        markup.add(types.InlineKeyboardButton('Вхід', callback_data='login'))
        markup.add(types.InlineKeyboardButton('Реєстрація', callback_data='registration'))
    else:
        if check_beehive_exists(chat_id):  # Передаємо chat_id
            markup.add(types.InlineKeyboardButton('Переглянути пасіку', callback_data='view_apiary'))
            markup.add(types.InlineKeyboardButton('Створити пасіку', callback_data='create_apiary'))
        else:
            markup.add(types.InlineKeyboardButton('Створити пасіку', callback_data='create_apiary'))

    bot.send_message(chat_id, "Виберіть опцію:", reply_markup=markup)

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
