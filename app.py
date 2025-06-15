from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import os

# ===============================
# CONFIGURAÇÕES DO BOT
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
    await update.message.reply_text("🚀 Bot de Arbitragem está online!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

# ===============================
# CONFIGURAÇÃO DO TELEGRAM
# ===============================

application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

# ===============================
# ROTA PARA O WEBHOOK
# ===============================

@app.route(f"/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        asyncio.run(application.process_update(update))
        return "ok"
    return "Webhook running!"

# ===============================
# ROTA PARA TESTE
# ===============================

@app.route("/")
def home():
    return "🚀 Bot de Arbitragem Rodando!"

# ===============================
# INICIANDO O APP
# ===============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
