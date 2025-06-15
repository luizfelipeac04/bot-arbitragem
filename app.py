from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio


# ==============================
# CONFIGURAÇÕES DO BOT
# ==============================

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# ==============================
# INICIALIZANDO O FLASK
# ==============================

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return '🤖 Bot de Arbitragem está rodando com sucesso!', 200


# ==============================
# FUNÇÕES DO BOT
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de Arbitragem está online e operando!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Buscando oportunidades de arbitragem (simulado)...")
    await asyncio.sleep(2)
    await update.message.reply_text("💰 Arbitragem encontrada! (exemplo)")


# ==============================
# FUNÇÃO PARA INICIAR O BOT
# ==============================

async def rodar_bot():
    app_bot = Application.builder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("status", status))
    app_bot.add_handler(CommandHandler("buscar", buscar))

    print("🚀 Bot iniciado com sucesso!")
    await app_bot.run_polling()


# ==============================
# INICIALIZAÇÃO GERAL
# ==============================

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(rodar_bot())

    port = int(os.environ.get('PORT', 8080))
    app_flask.run(host='0.0.0.0', port=port)
