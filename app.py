from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio


# ==========================
# CONFIGURAÇÕES
# ==========================

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "🤖 Bot está online e rodando com sucesso!", 200


# ==========================
# COMANDOS DO BOT
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de Arbitragem está online e funcionando!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot rodando perfeitamente!")

async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Buscando oportunidades de arbitragem (simulado)...")
    await asyncio.sleep(2)
    await update.message.reply_text("💰 Arbitragem encontrada! Simulação concluída.")

# ==========================
# FUNÇÃO PARA RODAR O BOT
# ==========================

async def main():
    app_bot = Application.builder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("status", status))
    app_bot.add_handler(CommandHandler("buscar", buscar))

    print("🚀 Bot iniciado com sucesso.")
    await app_bot.run_polling()


# ==========================
# EXECUTANDO BOT E FLASK
# ==========================

if __name__ == '__main__':
    asyncio.run(main())

    port = int(os.environ.get('PORT', 8080))
    app_flask.run(host='0.0.0.0', port=port)
