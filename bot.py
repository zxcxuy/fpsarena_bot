import telebot
from telebot import types
import sqlite3
from sqlite3 import Error
from google.colab import drive
import os

# Подключаем Google Drive
drive.mount('/content/drive')

# Путь к базе данных в Google Drive
DB_PATH = '/content/drive/MyDrive/fpsarena_bot_data/clients.db'

# Создаём папку, если её нет
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

TOKEN = '7847362610:AAG-hjbWWf4sV3XnLL80fJ9jMNq3iYza9-4'
bot = telebot.TeleBot(TOKEN)

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)  # Теперь БД в Google Drive
        print("Подключение к SQLite успешно")
        return conn
    except Error as e:
        print(f"Ошибка подключения к SQLite: {e}")
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL
            )
        ''')
        conn.commit()
        print("Таблица 'clients' создана или уже существует")
    except Error as e:
        print(f"Ошибка при создании таблицы: {e}")

def is_user_exists(conn, chat_id):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM clients WHERE chat_id = ?', (chat_id,))
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def add_client(conn, chat_id):
    try:
        if not is_user_exists(conn, chat_id):
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clients (chat_id) VALUES (?)', (chat_id,))
            conn.commit()
            print(f"Пользователь {chat_id} добавлен в базу данных")
        else:
            print(f"Пользователь {chat_id} уже есть в базе")
    except Error as e:
        print(f"Ошибка при добавлении пользователя: {e}")

# Подключаемся к БД (теперь она в Google Drive)
conn = create_connection()
if conn is not None:
    create_table(conn)
else:
    print("Ошибка: Не удалось подключиться к базе данных")

@bot.message_handler(commands=['start'])
def start(message):
    if conn is not None:
        add_client(conn, message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Прайсы💳')
    btn2 = types.KeyboardButton('Забронировать📆')
    btn3 = types.KeyboardButton('Акция🔔')
    markup.add(btn2, btn1, btn3)
    
    bot.send_message(
        message.chat.id,
        'Привет! Добро пожаловать в *FPS ARENA*🎮 \nНажми кнопку ниже, чтобы забронировать время.\
        \n━━━━━━━━━━━━━━━━━━━━━━━━━━\
        \nНаш канал с новостями: https://t.me/fpsarenamsk',
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop(message):
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE chat_id = ?', (message.chat.id,))
        conn.commit()
        bot.reply_to(message, "Вы удалены из базы данных. Возвращайтесь! 👋")
    else:
        bot.reply_to(message, "Ошибка: База данных не подключена")

@bot.message_handler(func=lambda message: True)
def main_handler(message):
    chat_id = message.chat.id
    if message.text == 'Прайсы💳':
        bot.send_photo(
            chat_id,
            photo="https://i.postimg.cc/CxpxM7sw-/price.jpg",
            caption='🌐 *Администратор:* @fpsarena\n📲 *Забронируй место прямо сейчас — пиши админу!*',
            parse_mode="Markdown"
        )
    elif message.text == 'Забронировать📆':
        bot.send_message(chat_id, 'Перейди по ссылке, чтобы забронировать 👉 https://t.me/fpsarena')
    elif message.text == 'Акция🔔':
        bot.send_photo(
            chat_id,
            photo="https://i.postimg.cc/ncDLtg7d/akc.jpg",
            caption='🎮 *ВРЕМЯ РАННИХ* 🎮\
            \n*Ежедневно с 8:00 до 14:00*\
            \n\n🔥 *Вы получаете 6 часов качественной игры по суперцене!* 🔥\
            \n\n💎 *FPS* — 300₽ (*50₽/час*)\
            \n💎 *FPS+* — 350₽ (*58₽/час*)\
            \n💎 *FPS ULTIMATE* — 400₽ (*67₽/час*)\
            \n\n🌇 *Идеальное время настало!*\
            \n\n❤️ *Начни свой день с *FPS ARENA*!* ✌🏻\
            \n\n⚡️ *Бронируй слот заранее и играй без очереди!*',
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, 'Такой команды нет. Воспользуйся кнопками ниже👻')

bot.infinity_polling()

# Закрываем соединение при завершении
if conn:
    conn.close()
