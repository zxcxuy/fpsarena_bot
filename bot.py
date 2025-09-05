import telebot
from telebot import types
from database import Database
import config
import sys

bot = telebot.TeleBot(config.TOKENS["main"])
db = Database()

USER_STATE = {}

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user
    firstname = user.first_name
    db.add_user(
        chat_id=message.chat.id,
        username=user.username,
        first_name=firstname,
        last_name=user.last_name,
    )
    try:
        bot.send_message(
            message.chat.id,
            f"Привет {firstname}! Добро пожаловать в *FPS ARENA*\U0001f3ae \n*Ты попал в то самое место, где можно оставаться наедине с игрой столько, сколько потребуется.*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\nНаш канал с новостями: https://t.me/fpsarenamsk",
            reply_markup=markuping(message.chat.id),
            parse_mode="Markdown",
        )
    except:
        bot.send_message(
            message.chat.id,
            f"Привет! Добро пожаловать в *FPS ARENA*\U0001f3ae \n*Ты попал в то самое место, где можно оставаться наедине с игрой столько, сколько потребуется.*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\nНаш канал с новостями: https://t.me/fpsarenamsk",
            reply_markup=markuping(message.chat.id),
            parse_mode="Markdown",
        )
    bot.send_message(
        message.chat.id,
        "\U0001f514 Если хотите не получать уведомления, отпишитесь от рассылки.",
    )

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.chat.id not in config.admins:
        bot.send_message(message.chat.id, "⛔ У вас нет доступа к админ-панели")
        return

    show_admin_menu(message.chat.id)

def show_admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    btn1 = types.KeyboardButton("1️⃣")
    btn2 = types.KeyboardButton("2️⃣")
    btn3 = types.KeyboardButton("3️⃣")
    btn4 = types.KeyboardButton("4️⃣")
    markup.add(btn1, btn2, btn3, btn4)

    menu_text = "👨‍💻 *Админ-панель FPS ARENA*\n\nВыберите действие:\n1️⃣ *Статистика* - общая статистика бота\n2️⃣ *Рассылка* - отправить сообщение всем\n3️⃣ *Последняя рассылка* - посмотреть последнюю рассылку\n4️⃣ *Назад* - вернуться в главное меню"

    bot.send_message(chat_id, menu_text, reply_markup=markup, parse_mode="Markdown")
    USER_STATE[chat_id] = "admin_menu"

@bot.message_handler(
    func=lambda message: message.text in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    and message.chat.id in config.admins
    and USER_STATE.get(message.chat.id) == "admin_menu"
)
def handle_admin_choice(message):
    chat_id = message.chat.id

    if message.text == "1️⃣":
        show_statistics(chat_id)
    elif message.text == "2️⃣":
        start_broadcast(chat_id)
    elif message.text == "3️⃣":
        show_broadcast_history(chat_id)
    elif message.text == "4️⃣":
        return_to_main(chat_id)

def show_statistics(chat_id):
    users_count = db.get_user_count()
    notify_users = db.get_user_notify_count()
    stats = f"*Всего пользователей:* {users_count}\n*Подписаны на рассылку:* {notify_users}\n*Охват:* {(notify_users/users_count*100 if users_count > 0 else 0):.1f}%"

    bot.send_message(chat_id, stats, parse_mode="Markdown")
    show_admin_menu(chat_id)

def show_broadcast_history(chat_id):
    try:
        history = db.get_last_broadcast_content(limit=1)
        
        if not history:
            bot.send_message(chat_id, "📝 История рассылок пуста")
            return
        
        item = history[0]
        history_text = "📊 Последняя рассылка:\n\n"
        history_text += f"📅 {item['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        history_text += f"📦 Тип: {item['content_type']}\n"
        if item['content_type'] == 'photo_text' and item['file_id']:
            history_text += f"🖼️ Есть фото\n"
        if item['content_text']:
            text_preview = item['content_text'][:100] + "..." if len(item['content_text']) > 100 else item['content_text']
            history_text += f"📝 Текст: {text_preview}\n"
        
        history_text += "━━━━━━━━━━━━━━━━━━━━\n"
        
        if item['file_id']:
            try:
                bot.send_photo(
                    chat_id, 
                    item['file_id'], 
                    caption=history_text, 
                    parse_mode="Markdown"
                )
            except:
                bot.send_message(chat_id, history_text + "\n🖼️ (Фото недоступно)")
        else:
            bot.send_message(chat_id, history_text)
        
        show_admin_menu(chat_id)    
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка при получении истории: {str(e)}")
        show_admin_menu(chat_id)

def start_broadcast(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_text = types.KeyboardButton("📝 Только текст")
    btn_photo = types.KeyboardButton("🖼️ Текст + фото")
    btn_cancel = types.KeyboardButton("❌ Отмена")
    markup.add(btn_text, btn_photo, btn_cancel)

    bot.send_message(
        chat_id,
        "📢 *Выберите тип рассылки:*\n\n• 📝 Только текст\n• 🖼️ Текст с фото",
        reply_markup=markup,
        parse_mode="Markdown",
    )
    USER_STATE[chat_id] = "choose_broadcast_type"

def return_to_main(chat_id):
    if chat_id in USER_STATE:
        del USER_STATE[chat_id]
    bot.send_message(
        chat_id, "Возвращаемся в главное меню...", reply_markup=markuping(chat_id)
    )

@bot.message_handler(
    func=lambda message: USER_STATE.get(message.chat.id) == "choose_broadcast_type"
    and message.chat.id in config.admins
)
def handle_broadcast_type(message):
    chat_id = message.chat.id

    if message.text == "❌ Отмена":
        del USER_STATE[chat_id]
        show_admin_menu(chat_id)
        return

    if message.text == "📝 Только текст":
        bot.send_message(
            chat_id,
            markdown_help,
            parse_mode="Markdown",
        )
        bot.send_message(
            chat_id,
            "📝 Введите текст для рассылки:",
            reply_markup=types.ForceReply(selective=True),
        )
        USER_STATE[chat_id] = "awaiting_text_broadcast"

    elif message.text == "🖼️ Текст + фото":
        bot.send_message(
            chat_id,
            "🖼️ Отправьте фото для рассылки:",
            reply_markup=types.ForceReply(selective=True),
        )
        USER_STATE[chat_id] = "awaiting_photo_broadcast"

@bot.message_handler(
    func=lambda message: USER_STATE.get(message.chat.id) == "awaiting_text_broadcast"
    and message.chat.id in config.admins,
    content_types=["text"],
)
def process_text_broadcast(message):
    chat_id = message.chat.id
    broadcast_text = message.text

    USER_STATE[chat_id] = {
        "type": "text",
        "text": broadcast_text,
        "state": "confirm_broadcast",
    }

    show_broadcast_confirmation(chat_id)

@bot.message_handler(
    func=lambda message: USER_STATE.get(message.chat.id) == "awaiting_photo_broadcast"
    and message.chat.id in config.admins,
    content_types=["photo"],
)
def process_photo_broadcast(message):
    chat_id = message.chat.id
    photo_id = message.photo[-1].file_id

    USER_STATE[chat_id] = {
        "type": "photo",
        "photo_id": photo_id,
        "state": "awaiting_photo_text",
    }

    bot.send_message(
        chat_id,
        markdown_help,
        parse_mode="Markdown",
    )
    bot.send_message(
        chat_id,
        "📝 Теперь введите текст для фото:",
        reply_markup=types.ForceReply(selective=True),
    )

@bot.message_handler(
    func=lambda message: isinstance(USER_STATE.get(message.chat.id), dict)
    and USER_STATE.get(message.chat.id).get("state") == "awaiting_photo_text"
    and message.chat.id in config.admins,
    content_types=["text"],
)
def process_photo_text(message):
    chat_id = message.chat.id
    broadcast_text = message.text

    USER_STATE[chat_id]["text"] = broadcast_text
    USER_STATE[chat_id]["state"] = "confirm_broadcast"

    show_broadcast_confirmation(chat_id)

def show_broadcast_confirmation(chat_id):
    broadcast_data = USER_STATE[chat_id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_confirm = types.KeyboardButton("✅ Начать рассылку")
    btn_cancel = types.KeyboardButton("❌ Отмена")
    markup.add(btn_confirm, btn_cancel)

    if broadcast_data["type"] == "photo":
        try:
            bot.send_photo(
                chat_id,
                broadcast_data["photo_id"],
                caption=broadcast_data["text"] + "\n\n\n*Превью рассылки*",
                parse_mode="Markdown",
                reply_markup=markup,
            )
        except:
            bot.send_photo(
                chat_id,
                broadcast_data["photo_id"],
                caption=broadcast_data["text"] + "\n\n\nПревью рассылки",
                reply_markup=markup,
            )
            bot.send_message(chat_id, "*Markdown* отключен", parse_mode="Markdown")
    else:
        try:
            bot.send_message(
                chat_id,
                broadcast_data["text"] + "\n\n\n*Превью рассылки*",
                parse_mode="Markdown",
                reply_markup=markup,
            )
        except:
            bot.send_message(
                chat_id,
                broadcast_data["text"] + "\n\n\nПревью рассылки",
                reply_markup=markup,
            )
            bot.send_message(chat_id, "*Markdown* отключен", parse_mode="Markdown")

@bot.message_handler(
    func=lambda message: isinstance(USER_STATE.get(message.chat.id), dict)
    and USER_STATE.get(message.chat.id).get("state") == "confirm_broadcast"
    and message.chat.id in config.admins
)
def confirm_broadcast(message):
    chat_id = message.chat.id
    broadcast_data = USER_STATE[chat_id]

    if message.text == "❌ Отмена":
        del USER_STATE[chat_id]
        show_admin_menu(chat_id)
        return

    if message.text == "✅ Начать рассылку":
        bot.send_message(chat_id, "Начинаю рассылку...")
        send_broadcast(chat_id, broadcast_data)
    else:
        show_broadcast_confirmation(chat_id)

def send_broadcast(admin_chat_id, broadcast_data):
    try:
        # content_id = db.save_broadcast_content(
        #     content_text=broadcast_data.get('text'),
        #     file_id=broadcast_data.get('photo_id')
        # )

        users = db.get_users_notify()
        # users = [{'chat_id':1291104485}]

        success_count = 0
        fail_count = 0

        for user in users:
            try:
                if broadcast_data["type"] == "text":
                    try:
                        bot.send_message(
                            user["chat_id"],
                            broadcast_data["text"],
                            parse_mode="Markdown"
                        )
                    except:
                        bot.send_message(user["chat_id"], broadcast_data["text"])
                else:
                    try:
                        bot.send_photo(
                            user["chat_id"],
                            broadcast_data["photo_id"],
                            caption=broadcast_data["text"],
                            parse_mode="Markdown"
                        )
                    except:
                        bot.send_photo(
                            user["chat_id"],
                            broadcast_data["photo_id"],
                            caption=broadcast_data["text"]
                        )

                success_count += 1

            except Exception as e:
                print(f"Ошибка отправки пользователю {user['chat_id']}: {e}")
                fail_count += 1

        report = f"""
✅ *Рассылка завершена!*

✔️ Успешно: {success_count}
❌ Не удалось: {fail_count}
📊 Всего: {success_count + fail_count}
"""
        bot.send_message(admin_chat_id, report, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(admin_chat_id, f"❌ Ошибка при рассылке: {e}")

    finally:
        if admin_chat_id in USER_STATE:
            del USER_STATE[admin_chat_id]
        show_admin_menu(admin_chat_id)

@bot.message_handler(func=lambda message: True)
def main_handler(message):
    chat_id = message.chat.id
    user = message.from_user

    db.add_user(
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    if message.text == "\U0001f4b3 Прайсы":
        bot.send_photo(
            chat_id,
            photo="https://i.postimg.cc/CxpxM7sw-/price.jpg",
            caption="\U0001f310 *Администратор:* @fpsarena\n\U0001f4f2 *Забронируй место прямо сейчас — пиши админу!*",
            parse_mode="Markdown",
        )
    elif message.text == "\U0001f4c5 Забронировать":
        bot.send_message(
            chat_id,
            "Перейди по ссылке, чтобы забронировать \U0001f449 https://t.me/fpsarena",
        )
    elif message.text == "\U00002b50 Акция":
        bot.send_photo(
            chat_id,
            photo="https://i.postimg.cc/HkWtMn1x/prom.jpg",
            caption="""
*Привет*🤠

🍁В преддверии осени радуем вас новым предложением!🍁

*5 часов с FPS ARENA —это хорошо, а 5+1 еще лучше*💯
Плати за 5 часов — *играй на час больше*😲

💥Победе нужно время!💥 Акция действует с 1 по 30 сентября 2025 года.
""",
            parse_mode="Markdown",
        )
    elif message.text == "\U0001f514 вкл/выкл рассылку":
        new_status = db.toggle_user_notify(chat_id)

        if new_status is not None:
            if new_status:
                bot.send_message(
                    chat_id,
                    "✅ *Рассылка включена!*\n\nВы будете получать уведомления о новых акциях и событиях FPS ARENA!",
                    parse_mode="Markdown",
                )
            else:
                bot.send_message(
                    chat_id,
                    "❌ *Рассылка отключена!*\n\nВы больше не будете получать уведомления о акциях.",
                    parse_mode="Markdown",
                )
        else:
            bot.send_message(
                chat_id,
                "⚠️ *Произошла ошибка!*\n\nНе удалось изменить настройки рассылки. Попробуйте позже.",
                parse_mode="Markdown",
            )
    else:
        bot.send_message(
            chat_id,
            "Такой команды нет. Воспользуйся кнопками ниже\U0001f47b\n(возможно обновление)",
            reply_markup=markuping(chat_id),
        )
        if USER_STATE:
            del USER_STATE[chat_id]

def markuping(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("\U0001f4b3 Прайсы")
    btn2 = types.KeyboardButton("\U0001f4c5 Забронировать")
    btn3 = types.KeyboardButton("\U00002b50 Акция")
    btn4 = types.KeyboardButton("\U0001f514 вкл/выкл рассылку")
    markup.add(btn2, btn1, btn3, btn4)
    if chat_id in config.admins:
        admin_btn = types.KeyboardButton("/admin")
        markup.add(admin_btn)
    return markup

markdown_help = r"""
📝 *ПОДСКАЗКА ПО РАЗМЕТКЕ:*

*Жирный текст* - \*текст\*
_Курсив_ - \_текст\_
`Моноширинный` - \`текст\`
[Ссылка](https://example.com) - \[текст](ссылка)

⚠️ *Внимание:* Закрывайте все специальные символы!
"""

def shutdown():
    """Завершение работы бота"""
    try:
        db.close()
        print("Пул соединений с БД закрыт при остановке бота")
    except Exception as e:
        print(f"Ошибка при закрытии соединений: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Ошибка в работе бота: {e}")
    finally:
        shutdown()