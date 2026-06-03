import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_TOKEN
from sheets import record_entrata, record_uscita

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Persistent reply keyboard shown after /start
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🟢 Entrata"), KeyboardButton("🔴 Uscita")]],
    resize_keyboard=True,
    is_persistent=True,
)


# --------------------------------------------------------------------------- #
#  /start
# --------------------------------------------------------------------------- #
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Benvenuto nel bot presenze!\n\n"
        "Usa i pulsanti qui sotto oppure i comandi:\n"
        "• /entrata — registra l'entrata\n"
        "• /uscita  — registra l'uscita e mostra la durata",
        reply_markup=MAIN_KEYBOARD,
    )


# --------------------------------------------------------------------------- #
#  Shared handlers
# --------------------------------------------------------------------------- #
async def handle_entrata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    result = record_entrata(user.id, user.username or user.first_name)

    if result["status"] == "already_open":
        await update.message.reply_text(
            f"⚠️ Hai già un'entrata aperta alle {result['timestamp']}.\n"
            "Registra prima l'uscita con /uscita o il pulsante 🔴 Uscita.",
            reply_markup=MAIN_KEYBOARD,
        )
    else:
        await update.message.reply_text(
            f"✅ Entrata registrata alle {result['timestamp']}",
            reply_markup=MAIN_KEYBOARD,
        )


async def handle_uscita(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    result = record_uscita(user.id)

    if result["status"] == "no_entrata":
        await update.message.reply_text(
            "⚠️ Nessuna entrata aperta trovata.\n"
            "Registra prima l'entrata con /entrata o il pulsante 🟢 Entrata.",
            reply_markup=MAIN_KEYBOARD,
        )
    else:
        await update.message.reply_text(
            f"👋 Uscita registrata alle {result['uscita']}\n"
            f"⏱ Durata sessione: {result['durata']}",
            reply_markup=MAIN_KEYBOARD,
        )


# --------------------------------------------------------------------------- #
#  Text button handler (maps button labels → same logic as commands)
# --------------------------------------------------------------------------- #
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🟢 Entrata":
        await handle_entrata(update, context)
    elif text == "🔴 Uscita":
        await handle_uscita(update, context)
    else:
        await update.message.reply_text(
            "Non ho capito. Usa i pulsanti o /entrata e /uscita.",
            reply_markup=MAIN_KEYBOARD,
        )


# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #
def main():
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("entrata", handle_entrata))
    app.add_handler(CommandHandler("uscita", handle_uscita))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot avviato. In attesa di messaggi...")
    app.run_polling()


if __name__ == "__main__":
    main()
