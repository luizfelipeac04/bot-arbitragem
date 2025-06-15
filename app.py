from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio


# ===============================
# CONFIGURAÇÕES
# ===============================

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)


# ===============================
# CONFIGURAÇÃO DO FLASK
# ===============================

app = Flask(__name__)


# ===============================
# FUNÇÕES DO BOT
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE!")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando corretamente!")


# ===============================
# CONFIGURAÇÃO DO TELEGRAM
# ===============================

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))


# ===============================
# PROCESSAMENTO DO WEBHOOK
# ===============================

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    loop = asyncio.get_event_loop()

    if not application.running:
        loop.run_until_complete(application.initialize())

    loop.run_until_complete(application.process_update(update))

    return 'ok'


# ===============================
# ROTA DE TESTE
# ===============================

@app.route('/')
def home():
    return "🚀 Bot de Arbitragem rodando com webhook no Railway!"


# ===============================
# INICIANDO O APP
# ===============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
