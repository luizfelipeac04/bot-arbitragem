from flask import Flask, request
import telegram
import threading
import time
import os
import requests

# =========================
# CONFIGURAÇÕES DO BOT
# =========================
TOKEN = 'SEU_TOKEN_DO_BOT_AQUI'
bot = telegram.Bot(token=TOKEN)

# 🔔 Coloque aqui o seu chat_id do Telegram para receber os alertas
SEU_CHAT_ID = 'SEU_CHAT_ID_AQUI'

# =========================
# INICIANDO O SERVIDOR FLASK
# =========================
app = Flask(__name__)

# =========================
# WEBHOOK – RECEBE COMANDOS DO TELEGRAM
# =========================
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text

    if text == '/start':
        bot.send_message(chat_id=chat_id, text="🤖 Bot de Arbitragem está online!")
    elif text == '/status':
        bot.send_message(chat_id=chat_id, text="📈 Estou monitorando arbitragem agora!")
    else:
        bot.send_message(chat_id=chat_id, text=f"Você disse: {text}")

    return 'ok'

# =========================
# FUNÇÃO DE ARBITRAGEM (EXEMPLO SIMPLES)
# =========================
def buscar_arbitragem():
    while True:
        try:
            # 🏟️ Aqui você colocaria sua lógica de busca de arbitragem
            # ➕ Exemplo fictício:
            oportunidades = ["Arbitragem encontrada no jogo XYZ 🤑"]

            for oportunidade in oportunidades:
                bot.send_message(chat_id=SEU_CHAT_ID, text=oportunidade)

            print("✅ Buscando arbitragem...")

        except Exception as e:
            print(f"❌ Erro na arbitragem: {e}")

        time.sleep(60)  # A cada 60 segundos faz nova busca


# =========================
# THREAD PARA ARBITRAGEM
# =========================
def iniciar_arb_thread():
    thread = threading.Thread(target=buscar_arbitragem)
    thread.start()


# =========================
# INICIALIZAÇÃO
# =========================
if __name__ == "__main__":
    iniciar_arb_thread()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
