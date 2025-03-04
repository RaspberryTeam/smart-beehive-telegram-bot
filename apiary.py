import requests

from bot_config import bot
from jwt_token import get_token
from telebot import types

from login import process_login


def view_apiary(message):  # Перегляд всіх пасік користувача
    from main import send_welcome, SERVER_CREATE_APIARY

    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()

    if get_token(chat_id) is None:
        bot.send_message(chat_id, "Спочатку авторизуйтеся")
        send_welcome(message)
    else:
        try:
            token = get_token(chat_id)
            headers = {"Authorization": f"Bearer " + token}

            response = requests.get(f"{SERVER_CREATE_APIARY}apiaries", headers=headers)

            if response.status_code == 200:

                apiaries = response.json()
                if apiaries:
                    for apiary in apiaries:
                        apiary_name = apiary.get('name', 'Без назви')
                        beehives_count = apiary.get('beehivesCount', 0)
                        apiary_id = apiary.get('id')
                        apiary_name = f"{apiary_name} ({beehives_count})"
                        markup.add(types.InlineKeyboardButton(apiary_name, callback_data=f"apiary_{apiary_id}"))
                    markup.add(types.InlineKeyboardButton('◀️Назад в меню◀️', callback_data='back_in_menu'))
                    bot.send_message(message.chat.id, "Ваші пасіки:", reply_markup=markup)
                else:
                    markup.add(types.InlineKeyboardButton('◀️Назад в меню◀️', callback_data='back_in_menu'))
                    bot.send_message(message.chat.id, "У вас ще немає жодної пасіки.", reply_markup=markup)

            elif response.status_code == 401:
                markup.add(types.InlineKeyboardButton('◀️Назад в меню◀️', callback_data='back_in_menu'))
                bot.send_message(message.chat.id, "Ви не авторизовані. Будь ласка, авторизуйтесь знову.",
                                 reply_markup=markup)
            else:
                markup.add(types.InlineKeyboardButton('◀️Назад в меню◀️', callback_data='back_in_menu'))
                bot.send_message(message.chat.id, f"Сталася невідома помилка. Код помилки: {response.status_code}",
                                 reply_markup=markup)

        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f"Помилка отримання даних: {e}")
            print(f"Помилка: {e}")
        except ValueError as e:
            bot.send_message(message.chat.id, "Помилка обробки даних з сервера.")
            print(f"Помилка JSON: {e}")


#Створення пасіки
def create_apiary(message):
    bot.send_message(message.chat.id, "Введіть назву пасіки:")
    bot.register_next_step_handler(message, get_nameApiary)


def get_nameApiary(message):
    from main import SERVER_CREATE_APIARY
    name_apiary = message.text
    chat_id = message.chat.id

    try:
        token = get_token(chat_id)
        headers = {"Authorization": f"Bearer " + token}

        response = requests.post(f"{SERVER_CREATE_APIARY}apiaries", json={"name": name_apiary}, headers=headers)
        if response.status_code == 201:
            bot.send_message(chat_id, "Пасіку створено!")
            from main import send_welcome
            send_welcome(message)
        else:
            bot.send_message(chat_id, f"Помилка при створені пасіки")
            bot.register_next_step_handler(message, process_login)
    except requests.exceptions.RequestException:
        bot.send_message(chat_id, f"Помилка підключення до сервера")
    except Exception:
        bot.send_message(chat_id, f"Помилка:")


######################################################################################
def check_beehive_exists():  # Перевірка на наявність пасік в користувача
    from main import SERVER_CREATE_APIARY

    response = requests.get(f"{SERVER_CREATE_APIARY}apiarys/")
    if response is None:
        return False
    else:
        return True


# Вивести всі вулики в пасіці
@bot.callback_query_handler(func=lambda call: call.data.startswith('apiary_'))
def apiary_details_handler(call):
    from main import send_welcome, SERVER_CREATE_APIARY
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup()
    apiary_id = call.data.split('_')[1]

    if get_token(chat_id) is None:
        bot.send_message(chat_id, "Спочатку авторизуйтеся")
        send_welcome(call.message)
        return

    try:
        token = get_token(chat_id)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{SERVER_CREATE_APIARY}apiaries/{apiary_id}", headers=headers)

        if response.status_code == 200:
            apiary_details = response.json()

            for i, beehive in enumerate(apiary_details.get('beehives', []), start=1):
                beehive_id = beehive.get('id')
                message_text = f"{i}) Вулик: {beehive.get('name', 'Без назви')}\n"
                markup.add(types.InlineKeyboardButton(message_text, callback_data=f"beehive_{beehive_id}"))

            markup.add(types.InlineKeyboardButton('➕Створити вулик➕', callback_data=f'create_beehive_{apiary_id}'))
            markup.add(types.InlineKeyboardButton('◀️Назад до пасік◀️', callback_data='view_apiary'))

            bot.send_message(chat_id, f"Деталі пасіки {apiary_details.get('name')}:\n", reply_markup=markup)
            bot.answer_callback_query(call.id)
        else:
            bot.send_message(chat_id, "Помилка при отриманні даних пасіки")
    except requests.exceptions.RequestException as e:
        print(e)
        bot.send_message(chat_id, "Сталася помилка при з'єднанні з сервером")

# Обробник кнопки для створення нового вулика
@bot.callback_query_handler(func=lambda call: call.data.startswith('create_beehive_'))
def create_beehive_handler(call):
    from create_beehive import request_beehive_name
    request_beehive_name(call)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('beehive_'))  # Виводим іфну про вулик
def beehive_details_handler(call):
    from main import send_welcome, SERVER_CREATE_APIARY
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup()
    if get_token(chat_id) is None:
        bot.send_message(chat_id, "Спочатку авторизуйтеся")
        send_welcome(call.message)
    else:
        try:
            token = get_token(chat_id)
            headers = {"Authorization": f"Bearer " + token}

            beehive_id = call.data.split('_')[1]
            details_response = requests.get(f"{SERVER_CREATE_APIARY}beehives/{beehive_id}", headers=headers)
            details_response.raise_for_status()
            beehive_details = details_response.json()

            message_text = f"Деталі вулика {beehive_details.get('name')}:\n"
            message_text += f"  - ID: {beehive_details.get('id')}\n"
            # message_text += f"  - Ключ: {beehive_details.get('beehive_key')}\n"
            message_text += f"  - Пасіка: {beehive_details.get('apiaryId')}\n"
            message_text += f"  - Створено: {beehive_details.get('createdAt')}\n"  # todo 1 Форматувати гарно вивід часу
            message_text += f"  - Оновлено: {beehive_details.get('updatedAt')}\n"

            # Перевірка наявності даних датчиків
            sensors_data = beehive_details.get('sensors_data', [])
            if sensors_data:
                message_text += "  - Дані датчиків:\n"
                for sensor_data in sensors_data:
                    message_text += f"    - {sensor_data}\n"
            else:
                message_text += "  - Дані датчиків відсутні.\n"

            markup.add(types.InlineKeyboardButton('◀️Назад до пасіки◀️', callback_data=f"apiary_{beehive_details.get('apiaryId')}"))
            bot.send_message(call.message.chat.id, message_text, reply_markup=markup)
            bot.answer_callback_query(call.id)

        except requests.exceptions.RequestException as e:
            print(e)
            bot.send_message(call.message.chat.id, "Помилка отримання даних про вулик.")
