import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "9034637875:AAGxfoTfhj6-oTlEopPTG4xw__ITQ3KwJN0"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8357304366  # Ваш Telegram ID (для /Adminhelp)
OWNER_ID = 7794924047  # Telegram ID второго пользователя (для /Ownerhelp)

def process_help_request(message, target_id, command_name):
    user_text = message.text.replace(f'/{command_name}', '').strip()
    
    if not user_text:
        bot.reply_to(message, f"❌ Пожалуйста, напишите ваше сообщение после команды.\nПример: `/{command_name} Нужна помощь`", parse_mode="Markdown")
        return

    username_text = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"
    
    report_message = (
        f"🚨 **Новое обращение к администрации ({command_name})!**\n\n"
        f"👤 **Отправитель:** {username_text}\n\n"
        f"💬 **Текст сообщения:**\n{user_text}"
    )

    keyboard = InlineKeyboardMarkup()
    # Передаем ID чата группы и ID сообщения для точного реплая в группе
    reply_button = InlineKeyboardButton(
        text="✍️ Ответить в группу", 
        callback_data=f"rep_{message.chat.id}_{message.message_id}"
    )
    keyboard.add(reply_button)

    bot.reply_to(message, "✅ Сообщение отправлено администрации.")

    try:
        bot.send_message(target_id, report_message, parse_mode="Markdown", reply_markup=keyboard)
    except Exception:
        pass

@bot.message_handler(commands=['Adminhelp'])
def handle_admin_help(message):
    process_help_request(message, ADMIN_ID, 'Adminhelp')

@bot.message_handler(commands=['Ownerhelp'])
def handle_owner_help(message):
    process_help_request(message, OWNER_ID, 'Ownerhelp')

@bot.callback_query_handler(func=lambda call: call.data.startswith('rep_'))
def ask_for_group_reply(call):
    _, chat_id, message_id = call.data.split('_')
    
    # Спрашиваем ответ у того админа, который нажал на кнопку
    msg = bot.send_message(call.from_user.id, "📝 Введите текст ответа. Бот отправит его в группу реплаем на сообщение пользователя:")
    bot.register_next_step_handler(msg, send_reply_to_group, chat_id, message_id)
    bot.answer_callback_query(call.id)

def send_reply_to_group(message, chat_id, message_id):
    if message.text.startswith('/'):
        bot.send_message(message.from_user.id, "❌ Отмена отправки ответа.")
        return

    try:
        # Отправляем ответ в группу в виде реплая на оригинальное сообщение
        bot.send_message(
            chat_id, 
            f"✉️ **Ответ от администрации:**\n\n{message.text}", 
            reply_to_message_id=int(message_id)
        )
        bot.send_message(message.from_user.id, "✅ Ответ успешно отправлен в группу!")
    except Exception:
        bot.send_message(message.from_user.id, "❌ Не удалось отправить ответ. Возможно, бот был удален из группы или сообщение пользователя удалено.")

if __name__ == '__main__':
    bot.infinity_polling()
