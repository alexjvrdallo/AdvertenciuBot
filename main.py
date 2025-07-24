import logging
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler
import os
import re
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warns = {}
usernames = {}

BAD_WORDS = [
    "puta", "mierda", "cabron", "imbecil", "idiota", "perra", "pendejo",
    "culiao", "marica", "verga", "coño", "hdp", "joder", "malparido"
]

def contains_bad_word(text):
    return any(re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) for word in BAD_WORDS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot de moderación activado.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    chat_id = update.message.chat_id

    # Detectar groserías
    if contains_bad_word(update.message.text):
        warns.setdefault(chat_id, {}).setdefault(user_id, 0)
        warns[chat_id][user_id] += 1
        count = warns[chat_id][user_id]

        await update.message.reply_text(f"⚠️ El @{username} tiene {count} advertencia(s).")

        # Notificar a admins cada 2 advertencias
        if count % 2 == 0:
            admins = await context.bot.get_chat_administrators(chat_id)
            for admin in admins:
                if not admin.user.is_bot:
                    await context.bot.send_message(admin.user.id, f"⚠️ El usuario @{username} ha recibido {count} advertencias.")

        # Silenciar cada 5 advertencias
        if count % 5 == 0:
            duration = 10 + ((count // 5) - 1) * 1
            until_date = datetime.utcnow() + timedelta(minutes=duration)
            await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False), until_date=until_date)
            await context.bot.send_message(chat_id, f"🔇 @{username} ha sido silenciado por {duration} minutos tras {count} advertencias.")

    # Verificar cambio de username
    old_username = usernames.get(user_id)
    current_username = update.message.from_user.username
    if old_username and old_username != current_username:
        await context.bot.send_message(chat_id, f"🔄 El usuario @{old_username} se cambió el nombre a @{current_username}.")
    usernames[user_id] = current_username

async def member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.chat_member.chat.id
    user = update.chat_member.from_user
    status = update.chat_member.new_chat_member.status
    if status == "member":
        if update.chat_member.old_chat_member.status in ["left", "kicked"]:
            admins = await context.bot.get_chat_administrators(chat_id)
            for admin in admins:
                if not admin.user.is_bot:
                    await context.bot.send_message(admin.user.id, f"🚪 El usuario @{user.username or user.first_name} ha vuelto al grupo.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatMemberHandler(member_update, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling()

if __name__ == "__main__":
    main()