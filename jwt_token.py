user_tokens = {}  # Словник для зберігання токенів користувачів

# Функція для збереження токена
def save_token(user_id, token):
    user_tokens[user_id] = token[1:-1]

# Отримання токена
def get_token(user_id):
    return user_tokens.get(user_id)
