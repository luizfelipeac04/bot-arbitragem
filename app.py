from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import time # Importar time para simulação de delay

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
# CHAT_ID não é estritamente necessário aqui, pois a resposta é para o chat_id do update
# mas é bom manter para referência ou se for enviar mensagens proativas
CHAT_ID = os.getenv("CHAT_ID") 

# ===============================
# FUNÇÕES DO BOT
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start."""
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE via Polling!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica o status do bot."""
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

async def buscar_arbitragem_simulada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simula uma busca de arbitragem e envia um alerta."""
    await update.message.reply_text("🔍 Buscando oportunidades de arbitragem (simulação)...")
    await asyncio.sleep(2) # Simula um delay na busca
    
    # Exemplo de oportunidade simulada
    oportunidade_simulada = (
        "💰 Arbitragem Encontrada! (Simulado)\n\n"
        "⚽️ Jogo: Time da Casa vs Time Visitante\n"
        "📈 Lucro Estimado: 3.5% (Simulado)\n\n"
        "🔹 Onde Apostar:\n"
        "🏠 Mandante: 2.10 na [Bet365](https://www.bet365.com/)\n"
        "🤝 Empate: 3.20 na [1xBet](https://1xbet.com/)\n"
        "🏃 Visitante: 3.50 na [Pinnacle](https://www.pinnacle.com/)\n\n"
        "Dica: Aposte R$100 para um lucro de R$3.50."
    )
    await update.message.reply_text(oportunidade_simulada, parse_mode='Markdown', disable_web_page_preview=True)


# ===============================
# INICIALIZANDO O BOT (Polling)
# ===============================
def main():
    """Inicia o bot e o modo polling."""
    # Constrói a aplicação do bot
    application = Application.builder().token(TOKEN).build()

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("buscar_simulado", buscar_arbitragem_simulada)) # Novo comando para simulação

    print("🚀 Bot rodando via Polling no Railway!")
    # Inicia o modo polling (o bot escuta por atualizações do Telegram)
    application.run_polling(poll_interval=1.0) # Verifica a cada 1 segundo por novas mensagens

if __name__ == '__main__':
    main()
