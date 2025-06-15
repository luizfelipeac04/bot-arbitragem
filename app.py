from flask import Flask, request
import telegram
import threading
import time
import os

# =========================
# CONFIGURAÇÕES DO BOT
# =========================
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telegram.Bot(token=TOKEN)

# =========================
# INICIANDO O SERVIDOR FLASK
# =========================
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.lower()

    if text == '/start':
        bot.send_message(chat_id=chat_id, text="🤖 Bot de Arbitragem está online!")
    elif text == '/status':
        bot.send_message(chat_id=chat_id, text="📈 O bot está funcionando corretamente!")
    else:
        bot.send_message(chat_id=chat_id, text=f"❓ Comando não reconhecido: {text}")

    return 'ok'

# =========================
# FUNÇÃO DE ARBITRAGEM (EXEMPLO SIMPLES)
# =========================
def buscar_arbitragem():
    while True:
        try:
            oportunidade = "🔥 Arbitragem encontrada no jogo TESTE FC vs DEMO FC 🤑"

            bot.send_message(chat_id=CHAT_ID, text=oportunidade)

            print("✅ Arbitragem enviada com sucesso.")

        except Exception as e:
            print(f"❌ Erro na arbitragem: {e}")

        time.sleep(60)

# =========================
# THREAD PARA ARBITRAGEM
# =========================
def iniciar_arb_thread():
    thread = threading.Thread(target=buscar_arbitragem)
    thread.daemon = True
    thread.start()

# =========================
# INICIALIZAÇÃO
# =========================
if __name__ == "__main__":
    iniciar_arb_thread()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
