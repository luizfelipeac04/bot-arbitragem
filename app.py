from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import threading
import os

# =========================
# CONFIGURAÇÕES DO BOT
# =========================
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# =========================
# INICIALIZANDO O FLASK
# =========================
app = Flask(__name__)

# =========================
# FUNÇÕES DO BOT
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot de Arbitragem está online!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 O bot está funcionando corretamente!")

# =========================
# ARBITRAGEM SIMULADA
# =========================
async def buscar_arbitragem(app_bot: Application):
    while True:
        try:
            texto = "🔥 Arbitragem encontrada no jogo TESTE FC vs DEMO FC 🤑"
            await app_bot.bot.send_message(chat_id=CHAT_ID, text=texto)
            print("✅ Arbitragem enviada com sucesso.")
        except Exception as e:
            print(f"❌ Erro na arbitragem: {e}")
        await asyncio.sleep(60)  # Intervalo de 60 segundos

# =========================
# WEBHOOK – RECEBE COMANDOS
# =========================
@app.route('/webhook', methods=['POST'])
def webhook():
    return 'OK'  # Apenas para manter ativo, comandos são via polling

# =========================
# INICIALIZAÇÃO DO BOT
# =========================
def iniciar_bot():
    app_bot = Application.builder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("status", status))

    loop = asyncio.get_event_loop()

    # Thread para buscar arbitragem
    loop.create_task(buscar_arbitragem(app_bot))

    print("🤖 Bot iniciado com sucesso.")
    app_bot.run_polling()

# =========================
# THREAD PARA O BOT
# =========================
def iniciar_thread_bot():
    thread = threading.Thread(target=iniciar_bot)
    thread.daemon = True
    thread.start()

# =========================
# INICIANDO TUDO
# =========================
if __name__ == '__main__':
    iniciar_thread_bot()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
