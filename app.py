from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import threading
import os


# ==============================
# CONFIGURAÇÕES DO BOT
# ==============================

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# ==============================
# INICIALIZANDO O FLASK
# ==============================

app = Flask(__name__)


# ==============================
# FUNÇÕES DO BOT
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de Arbitragem está online!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

async def buscar_arbitragem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Buscando oportunidades de arbitragem...")

# ==============================
# WEBHOOK FLASK
# ==============================

@app.route('/')
def webhook():
    return 'Bot de Arbitragem está rodando!', 200


# ==============================
# FUNÇÃO PARA INICIAR O BOT
# ==============================

def iniciar_bot():
    app_bot = Application.builder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("status", status))
    app_bot.add_handler(CommandHandler("buscar", buscar_arbitragem))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app_bot.run_polling())

# ==============================
# THREAD PARA EXECUTAR O BOT
# ==============================

def iniciar_thread_bot():
    bot_thread = threading.Thread(target=iniciar_bot)
    bot_thread.start()

# ==============================
# EXECUTANDO O FLASK + BOT
# ==============================

if __name__ == '__main__':
    iniciar_thread_bot()
    app.run(host='0.0.0.0', port=8080)
