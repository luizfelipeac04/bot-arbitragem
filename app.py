from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import time
import threading # Vamos usar threading para a busca em background

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDS_API_KEY") # Não usado na simulação

SPORT = 'soccer'
REGION = 'us,eu,uk,au'
MARKETS = 'h2h'
BOOKMAKERS_LIMIT = 5
MIN_PROFIT_PERCENT = 1.0
SEARCH_INTERVAL_SECONDS = 1800 # 30 minutos

BOOKMAKERS_LINKS = {
    'Bet365': 'https://www.bet365.com/',
    'Betfair': 'https://www.betfair.com/',
    'Pinnacle': 'https://www.pinnacle.com/',
    'Unibet': 'https://www.unibet.com/',
    'Matchbook': 'https://www.matchbook.com/',
    'Betano': 'https://www.betano.com/',
    '1xBet': 'https://1xbet.com/',
    'Sportingbet': 'https://www.sportingbet.com/',
    'Bodog': 'https://www.bodog.com/',
    'Betway': 'https://www.betway.com/',
    'Rivalo': 'https://www.rivalo.com/',
    'LeoVegas': 'https://www.leovegas.com/',
    '888sport': 'https://www.888sport.com/',
    'Mr Green': 'https://www.mrgreen.com/',
    'Betfred': 'https://www.betfred.com/',
    'Parimatch': 'https://www.parimatch.com/',
    'Coolbet': 'https://www.coolbet.com/',
    'DraftKings': 'https://www.draftkings.com/',
    'FanDuel': 'https://www.fanduel.com/',
    'Bwin': 'https://www.bwin.com/',
    'William Hill': 'https://www.williamhill.com/',
    'Marathonbet': 'https://www.marathonbet.com/',
    '10bet': 'https://www.10bet.com/',
    'Betcris': 'https://www.betcris.com/',
    'KTO': 'https://www.kto.com/',
}

alerted_opportunities = set()

# Instância global do Bot e Application
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# ===============================
# FUNÇÕES DE CÁLCULO DE ARBITRAGEM (ainda presentes para formatação)
# ===============================
def calculate_arbitrage_profit(odds):
    inverse_sum = sum(1 / odd for odd in odds)
    if inverse_sum < 1:
        profit_percent = (1 - inverse_sum) * 100
        return profit_percent
    return 0

def format_arbitrage_message(game, best_odds_info, profit_percent):
    home_team = game['home_team']
    away_team = game['away_team']
    commence_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    sport_name = game.get('sport_title', 'Futebol (Simulado)') 

    message = (
        f"💰 *Arbitragem Encontrada!* \n\n"
        f"⚽️ *Jogo:* {home_team} vs {away_team}\n"
        f"📅 *Data:* {commence_time_str}\n"
        f"🏆 *Esporte:* {sport_name}\n" 
        f"📈 *Lucro Garantido:* {profit_percent:.2f}%\n\n"
        f"🔹 *Onde Apostar:*\n"
    )

    for outcome_name, odd_data in best_odds_info.items():
        bookmaker = odd_data['bookmaker']
        link = BOOKMAKERS_LINKS.get(bookmaker, f"https://www.google.com/search?q={bookmaker}")
        
        label = outcome_name
        if outcome_name == 'home':
            label = '🏠 Mandante'
        elif outcome_name == 'draw':
            label = '🤝 Empate'
        elif outcome_name == 'away':
            label = '🏃 Visitante'
            
        message += f"{label}: *{odd_data['odd']:.2f}* na [{bookmaker}]({link})\n"
        
    return message

# ===============================
# FUNÇÕES DO BOT TELEGRAM
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem (Simulação) está ONLINE via Webhook e buscando oportunidades automaticamente! Use /status para checar.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ O bot está funcionando corretamente e buscando oportunidades a cada {SEARCH_INTERVAL_SECONDS / 60:.0f} minutos (Simulação).")

# ===============================
# LÓGICA PRINCIPAL DE BUSCA DE ARBITRAGEM (SIMULADA INTERNAMENTE - AGORA COM THREADING)
# ===============================
def find_and_alert_arbitrage_loop_simulated_threaded():
    """Função que roda a busca simulada em uma thread separada."""
    # Criamos um novo loop de eventos para esta thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    simulated_game_id_counter = 0

    while True:
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Seu bot está PROCURANDO OPORTUNIDADES (SIMULAÇÃO), aguarde...") 
        try:
            simulated_game_id_counter += 1
            game_id_unique = f"SIM-{simulated_game_id_counter}-{time.time()}"
            
            game_simulado = {
                'id': game_id_unique,
                'home_team': 'Time Simulado A',
                'away_team': 'Time Simulado B',
                'commence_time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'sport_title': 'Futebol (Simulado)'
            }
            best_odds_info_simulado = {
                'home': {'odd': 2.10, 'bookmaker': 'Bet365'},
                'draw': {'odd': 3.50, 'bookmaker': '1xBet'},
                'away': {'odd': 3.10, 'bookmaker': 'Pinnacle'}
            }
            odds_list_simulado = [2.10, 3.50, 3.10]
            
            profit_simulado = calculate_arbitrage_profit(odds_list_simulado)
            
            if game_id_unique in alerted_opportunities:
                print("Oportunidade simulada já alertada. Pulando.")
                time.sleep(SEARCH_INTERVAL_SECONDS) # time.sleep para threading
                continue 
            
            if profit_simulado >= MIN_PROFIT_PERCENT:
                message = format_arbitrage_message(game_simulado, best_odds_info_simulado, profit_simulado)
                
                if CHAT_ID:
                    # Usamos application.bot.send_message. É assíncrono, então precisa ser awaited.
                    # Mas estamos em uma thread, então precisamos do loop da thread.
                    loop.run_until_complete(application.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True))
                    alerted_opportunities.add(game_id_unique)
                    print(f"✅ Alerta de arbitragem SIMULADA enviado! Lucro: {profit_simulado:.2f}%")
                else:
                    print(f"Alerta de arbitragem SIMULADA encontrado, mas CHAT_ID não configurado. Lucro: {profit_simulado:.2f}%")
            else:
                print(f"Oportunidade de arbitragem SIMULADA encontrada, mas lucro ({profit_simulado:.2f}%) abaixo do mínimo ({MIN_PROFIT_PERCENT}%)")

        except Exception as e:
            print(f"❌ Erro inesperado na busca de arbitragem (SIMULAÇÃO): {e}")
        
        time.sleep(SEARCH_INTERVAL_SECONDS) # time.sleep para threading

# ===============================
# ROTAS DO FLASK PARA O WEBHOOK E TESTE
# ===============================
app_flask = Flask(__name__)

@app_flask.route('/webhook', methods=['POST'])
async def webhook():
    """Rota que o Telegram envia as atualizações."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        await application.process_update(update) # Processa a atualização do Telegram
        return "ok"
    return "Webhook running!"

@app_flask.route('/')
def home():
    """Rota de teste para verificar se o servidor está ativo."""
    return "🚀 Bot de Arbitragem está rodando com Webhook no Railway! Servidor Flask OK."

# ===============================
# PONTO DE ENTRADA PRINCIPAL PARA O RAILWAY
# = =============================
# Inicia os handlers do bot
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

if __name__ == '__main__':
    print("🚀 Iniciando aplicação Railway (Webhook com Threading) FINAL...")

    # Inicializa a aplicação do Telegram para processar os updates via webhook
    # Esta linha é crucial para o run_webhook funcionar
    asyncio.get_event_loop().run_until_complete(application.initialize())

    # Inicia a busca simulada em uma thread separada.
    # Esta thread terá seu próprio loop de eventos para as operações assíncronas de envio.
    search_thread = threading.Thread(target=find_and_alert_arbitrage_loop_simulated_threaded)
    search_thread.daemon = True # Permite que a thread principal encerre o programa se ela parar
    search_thread.start()

    # Inicia o servidor Flask usando Application.run_webhook.
    # Este método gerencia o servidor Flask e o loop de eventos para o bot.
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path="/webhook"
    )
