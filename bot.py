import telebot
from telebot import types

TOKEN = '7847362610:AAG-hjbWWf4sV3XnLL80fJ9jMNq3iYza9-4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Прайсы💳')
    btn2 = types.KeyboardButton('Забронировать📆')
    btn3 = types.KeyboardButton('Акция🔔')
    markup.add(btn2, btn1, btn3)
    bot.send_message(message.chat.id,
                    'Привет! Добро пожаловать в *FPS ARENA*🎮 \nНажми кнопку ниже, чтобы забронировать время.\
                        \n━━━━━━━━━━━━━━━━━━━━━━━━━━\
                        \nНаш канал с новостями: https://t.me/fpsarenamsk',
                    reply_markup=markup,
                    parse_mode="Markdown")
@bot.message_handler(func=lambda message: True)
def main_handler(message):
    chat_id = message.chat.id
    if message.text == 'Прайсы💳':
        bot.send_photo(chat_id, photo="https://i.postimg.cc/CxpxM7sw-/price.jpg", caption='🌐 *Администратор:* @fpsarena\
                        \n📲 *Забронируй место прямо сейчас — пиши админу!*',
                        parse_mode="Markdown")
    elif message.text == 'Забронировать📆':
        bot.send_message(chat_id, 'Перейди по ссылке, чтобы забронировать 👉 https://t.me/fpsarena')
    elif message.text == 'Акция🔔':
        bot.send_photo(chat_id, photo="https://i.postimg.cc/ncDLtg7d/akc.jpg", caption='🎮 *ВРЕМЯ РАННИХ* 🎮\
                        \n*Ежедневно с 8:00 до 14:00*\
                        \n\n🔥 *Вы получаете 6 часов качественной игры по суперцене!* 🔥\
                        \n\n💎 *FPS* — 300₽ (*50₽/час*)\
                        \n💎 *FPS+* — 350₽ (*58₽/час*)\
                        \n💎 *FPS ULTIMATE* — 400₽ (*67₽/час*)\
                        \n\n🌇 *Идеальное время настало!*\
                        \n\n❤️ *Начни свой день с *FPS ARENA*!* ✌🏻\
                        \n\n⚡️ *Бронируй слот заранее и играй без очереди!* ',
                        parse_mode="Markdown")
    else:
        bot.send_message(chat_id, 'Такой команды нет. Воспользуйся кнопками ниже👻')

bot.infinity_polling()
