import requests
import telebot
import re
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from jwt_token import save_token
from bot_config import bot

SERVER_REG = "https://smart-beehive-server.onrender.com/api/users"


def process_registration(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("📱 Надіслати номер телефону", request_contact=True)
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Будь ласка, надішліть свій номер телефону через кнопку або введіть його вручну (9 цифр без '+38').",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, ask_registration_password)


def ask_registration_password(message):
    if message.contact:
        phone = message.contact.phone_number[-9:]
    else:
        phone = message.text.strip()
        if not re.fullmatch(r"\d{9}", phone):
            bot.send_message(message.chat.id, "Невірний формат! Введіть номер із 9 цифр (наприклад, 931234567):")
            return bot.register_next_step_handler(message, ask_registration_password)

    bot.send_message(message.chat.id, "Введіть пароль для реєстрації (мінімум 8 символів):",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, register_user, phone)


def register_user(message, phone):
    chat_id = message.chat.id
    password = message.text.strip()

    if len(password) < 7:
        bot.send_message(chat_id, "Пароль має бути мінімум 8 символів. Введіть ще раз:")
        bot.register_next_step_handler(message, register_user, phone)
        return

    try:
        response = requests.post(SERVER_REG, json={"phonenumber": phone, "password": password}, timeout=10)

        from main import send_welcome
        if response.status_code == 201:
            save_token(chat_id, response.text)
            bot.send_message(chat_id, "✅ Реєстрація успішна! Ось ваше меню:")
            send_welcome(message)
        elif response.status_code == 400:
            bot.send_message(chat_id, "⚠️ Такий користувач уже існує.")
            send_welcome(message)
        else:
            bot.send_message(chat_id, "❌ Помилка реєстрації.")
            send_welcome(message)

    except requests.exceptions.Timeout:
        bot.send_message(chat_id, "⏳ Сервер не відповідає. Спробуйте пізніше.")
        bot.register_next_step_handler(message, process_registration)

    except requests.exceptions.RequestException as e:
        bot.send_message(chat_id, f"❌ Помилка запиту: {e}")
        bot.register_next_step_handler(message, process_registration)

# def process_registration(message):
#     bot.send_message(message.chat.id, "Введіть ваш номер телефону:")
#     bot.register_next_step_handler(message, ask_registration_password)
#
# def ask_registration_password(message):
#     chat_id = message.chat.id
#     phone = message.text
#     bot.send_message(chat_id, "Введіть пароль для реєстрації:")
#     bot.register_next_step_handler(message, register_user, phone)
#
# def register_user(message, phone):
#     chat_id = message.chat.id
#     password = message.text
#
#     try:
#         response = requests.post(f"{SERVER_REG}", json={"phonenumber": phone, "password": password},
#                                  timeout=10)
#
#         from main import send_welcome
#         if response.status_code == 201:
#             save_token(message.chat.id, response.text)
#             bot.send_message(chat_id, "Реєстрація успішна! Ось ваше меню:")
#             send_welcome(message)
#         elif response.status_code == 400:
#             bot.send_message(chat_id, f"Такий користувач уже існує.")
#             send_welcome(message)
#         else:
#             bot.send_message(chat_id, f"Помилка реєстрації.")
#             send_welcome(message)
#
#     except requests.exceptions.Timeout:
#         bot.send_message(chat_id, "Сервер не відповідає. Спробуйте пізніше.")
#         bot.register_next_step_handler(message, process_registration)
#         return
#
#     except requests.exceptions.RequestException as e:
#         bot.send_message(chat_id, f"Помилка запиту: {e}")
#         bot.register_next_step_handler(message, process_registration)



