import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

TOKEN = '7568390894:AAELswDagoZKnQAGznKwLg49dD6jEsq4OUU'
API_URL = f'https://api.telegram.org/bot{TOKEN}/'

# База данных
DB = {
    'users': {},
    'products': {},
    'orders': {},
    'cart': {}
}

# Функции для работы с базой данных
def save_db():
    try:
        if not os.path.exists('database'):
            os.makedirs('database')
        with open('database/market.json', 'w', encoding='utf-8') as f:
            json.dump(DB, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения БД: {e}")

def load_db():
    global DB
    try:
        if os.path.exists('database/market.json'):
            with open('database/market.json', 'r', encoding='utf-8') as f:
                DB = json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки БД: {e}")

def call_telegram(method, params=None):
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/{method}'
        if params:
            data = urllib.parse.urlencode(params).encode()
            req = urllib.request.Request(url, data=data)
        else:
            req = urllib.request.Request(url)
        
        return json.loads(urllib.request.urlopen(req).read().decode())
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None

def send_message(chat_id, text, keyboard=None):
    try:
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if keyboard:
            params['reply_markup'] = json.dumps(keyboard)
        
        return call_telegram('sendMessage', params)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def send_file(chat_id, file_path):
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Формируем multipart/form-data запрос
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
            f'{chat_id}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="document"; filename="{os.path.basename(file_path)}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n'
        ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()
        
        req = urllib.request.Request(url, data=body, headers=headers)
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode())
    except Exception as e:
        print(f"Ошибка отправки файла: {e}")
        return None

def get_updates(offset=0):
    try:
        params = {
            'offset': offset,
            'timeout': 30
        }
        return call_telegram('getUpdates', params)['result']
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
        return []

def get_keyboard():
    return {
        'keyboard': [
            ['🛍 Товары', '🔍 Поиск'],
            ['🛒 Корзина', '📦 Мои заказы'],
            ['💰 Баланс', '👤 Профиль']
        ],
        'resize_keyboard': True
    }

def get_products_keyboard():
    products = get_available_products()
    keyboard = {
        'inline_keyboard': []
    }
    for product in products:
        keyboard['inline_keyboard'].append([
            {
                'text': f"{product['name']} - {product['price']} RUB",
                'callback_data': f"add_{product['name']}"
            }
        ])
    return keyboard

def get_cart_keyboard():
    return {
        'inline_keyboard': [
            [
                {
                    'text': "🛒 Купить всё",
                    'callback_data': "buy_all"
                }
            ]
        ]
    }

def handle_user(message):
    try:
        user_id = str(message['from']['id'])
        if user_id not in DB['users']:
            DB['users'][user_id] = {
                'username': message['from'].get('username', ''),
                'balance': 0,  # Начальный баланс
                'cart': [],
                'orders': []
            }
            save_db()
        return True
    except Exception as e:
        print(f"Ошибка обработки пользователя: {e}")
        return False

def get_available_products():
    products = []
    try:
        if os.path.exists('tov'):
            for filename in os.listdir('tov'):
                if filename.endswith('.json'):
                    with open(os.path.join('tov', filename), 'r', encoding='utf-8') as f:
                        product = json.load(f)
                        product['filename'] = filename  # Сохраняем имя файла
                        products.append(product)
    except Exception as e:
        print(f"Ошибка чтения товаров: {e}")
    return products

def add_to_cart(user_id, product_name):
    products = get_available_products()
    product = next((p for p in products if p['name'] == product_name), None)
    if product:
        DB['users'][user_id]['cart'].append(product)
        save_db()
        return True
    return False

def buy_cart(user_id):
    user = DB['users'][user_id]
    total_price = sum(p['price'] for p in user['cart'])
    if user['balance'] >= total_price:
        user['balance'] -= total_price
        
        # Отправляем файлы только для текущей покупки
        for product in user['cart']:
            file_path = product.get('file')
            if file_path and os.path.exists(file_path):
                send_file(user_id, file_path)  # Отправляем файл
            else:
                print(f"Файл для товара '{product['name']}' не найден.")
        
        # Удаляем товары из папки tov после покупки
        for product in user['cart']:
            file_path = os.path.join('tov', product['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Очищаем корзину
        user['cart'] = []
        save_db()
        return True
    return False

def print_flipper_zero():
    orange = '\033[38;5;78m'  
    text = """
     ____.             .__    _________.__                   
    |    | ____ _____  |  |  /   _____/|  |__   ____ ______  
    |    |/ __ \\__  \ |  |  \_____  \ |  |  \ /  _ \\____ \ 
/\__|    \  ___/ / __ \|  |__/        \|   Y  (  <_> )  |_> >
\________|\___  >____  /____/_______  /|___|  /\____/|   __/ 
              \/     \/             \/      \/       |__|    """

    print(text)

def main():
    try:
        print_flipper_zero()
        
        print("\033[93mИнициализация сервера...\033[0m")
        for i in range(31):
            progress = i / 30 * 29.3
            bar = "=" * i + " " * (30-i)
            print(f"\r[{bar}] {progress:.1f}mb/29.3mb", end="")
            time.sleep(0.1)
        print("\n\033[92mСервер запущен!\033[0m")
        
        if not os.path.exists('database'):
            os.makedirs('database')
        
        load_db()
        offset = 0
        
        while True:
            try:
                updates = get_updates(offset)
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    # Обработка callback-запросов
                    if 'callback_query' in update:
                        callback_query = update['callback_query']
                        chat_id = callback_query['message']['chat']['id']
                        user_id = str(callback_query['from']['id'])
                        data = callback_query['data']
                        
                        if data.startswith('add_'):
                            product_name = data.split('_')[1]
                            if add_to_cart(user_id, product_name):
                                send_message(chat_id, f"✅ Товар '{product_name}' добавлен в корзину!")
                            else:
                                send_message(chat_id, "❌ Товар не найден.")
                        
                        elif data == 'buy_all':
                            if buy_cart(user_id):
                                send_message(chat_id, "✅ Все товары куплены! Файлы отправлены.")
                            else:
                                send_message(chat_id, "❌ Недостаточно средств на балансе.")
                        continue
                    
                    if 'message' not in update:
                        continue
                    
                    message = update['message']
                    if 'text' not in message:
                        continue
                    
                    chat_id = message['chat']['id']
                    user_id = str(message['from']['id'])
                    text = message['text']
                    
                    if not handle_user(message):
                        continue
                    
                    if text == '/start':
                        send_message(chat_id, "🏪 Добро пожаловать в JealShop🦜!", get_keyboard())
                    
                    elif text == '🛍 Товары':
                        products = get_available_products()
                        if products:
                            send_message(chat_id, "🛍 Выберите товар:", get_products_keyboard())
                        else:
                            send_message(chat_id, "😕 Пока нет доступных товаров")
                        
                    elif text == '🔍 Поиск':
                        send_message(chat_id, "🔍 Введите название товара")
                        
                    elif text == '🛒 Корзина':
                        user = DB['users'][user_id]
                        if user['cart']:
                            cart_text = "🛒 Ваша корзина:\n"
                            cart_text += "\n".join([f"{p['name']} - {p['price']} RUB" for p in user['cart']])
                            cart_text += f"\n\nИтого: {sum(p['price'] for p in user['cart'])} RUB"
                            send_message(chat_id, cart_text, get_cart_keyboard())
                        else:
                            send_message(chat_id, "🛒 Корзина пуста")
                        
                    elif text == '📦 Мои заказы':
                        user = DB['users'][user_id]
                        if user['orders']:
                            orders_text = "📦 Ваши заказы:\n"
                            orders_text += "\n".join([f"{p['name']} - {p['price']} RUB" for p in user['orders']])
                            send_message(chat_id, orders_text)
                        else:
                            send_message(chat_id, "📦 У вас пока нет заказов")
                        
                    elif text == '💰 Баланс':
                        user = DB['users'][user_id]
                        send_message(chat_id, f"💰 Ваш баланс: {user['balance']} RUB")
                        
                    elif text == '👤 Профиль':
                        user = DB['users'][user_id]
                        profile_text = f"""👤 Ваш профиль:
ID: {user_id}
Username: @{user['username']}
Баланс: {user['balance']} RUB
Заказов: {len(user['orders'])}"""
                        send_message(chat_id, profile_text)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"\033[91mОшибка: {e}\033[0m")
                time.sleep(5)
                
    except Exception as e:
        print(f"\033[91mКритическая ошибка: {e}\033[0m")

main()