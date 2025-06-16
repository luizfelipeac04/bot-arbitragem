from flask import Flask, request # Importar Flask para o Webhook
from telegram import Bot, Update # Importar Bot e Update
from telegram.ext import Application, CommandHandler, ContextTypes # Importar Application, CommandHandler, ContextTypes
import os # Para acessar variáveis de ambiente
import asyncio # Para tarefas assíncronas
import time # Para simular delay e timestamps

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN") # Token do bot do Telegram
CHAT_ID = os.getenv("CHAT_ID") # ID do chat para enviar alertas
API_KEY = os.getenv("ODDS_API_KEY") # Chave da The Odds API (não usada na simulação)

SPORT = 'soccer' # Esporte para simulação e futura integração real
REGION = 'us,eu,uk,au' # Regiões (não usada na simulação)
MARKETS = 'h2h' # Mercado (não usado na simulação)
BOOKMAKERS_LIMIT = 5 # Limite de casas (não usado na simulação)
MIN_PROFIT_PERCENT = 1.0 # Lucro mínimo para alerta (usado na simulação)
SEARCH_INTERVAL_SECONDS = 1800 # Intervalo da busca automática (30 minutos)

# Dicionário de casas de apostas com links (para mensagens bonitas)
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

alerted_opportunities = set() # Cache para evitar alertas repetidos

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
    commence_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) # Usar hora atual para simulação

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
# FUNÇÕES DO BOT TELEGRAM (para Webhook)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem (Simulação) está ONLINE via Webhook e buscando oportunidades automaticamente! Use /status para checar.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ O bot está funcionando corretamente e buscando oportunidades a cada {SEARCH_INTERVAL_SECONDS / 60:.0f} minutos (Simulação).")

# ===============================
# LÓGICA PRINCIPAL DE BUSCA DE ARBITRAGEM (SIMULADA INTERNAMENTE)
# ===============================
async def find_and_alert_arbitrage_loop_simulated():
    """Loop contínuo para buscar por oportunidades de arbitragem SIMULADAS e enviar alertas."""
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
                await asyncio.sleep(SEARCH_INTERVAL_SECONDS)
                continue 
            
            if profit_simulado >= MIN_PROFIT_PERCENT:
                message = format_arbitrage_message(game_simulado, best_odds_info_simulado, profit_simulado)
                
                if CHAT_ID:
                    await application.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
                    alerted_opportunities.add(game_id_unique)
                    print(f"✅ Alerta de arbitragem SIMULADA enviado! Lucro: {profit_simulado:.2f}%")
                else:
                    print(f"Alerta de arbitragem SIMULADA encontrado, mas CHAT_ID não configurado. Lucro: {profit_simulado:.2f}%")
            else:
                print(f"Oportunidade de arbitragem SIMULADA encontrada, mas lucro ({profit_simulado:.2f}%) abaixo do mínimo ({MIN_PROFIT_PERCENT}%)")

        except Exception as e:
            print(f"❌ Erro inesperado na busca de arbitragem (SIMULAÇÃO): {e}")
        
        await asyncio.sleep(SEARCH_INTERVAL_SECONDS) 

# ===============================
# ROTAS DO FLASK PARA O WEBHOOK E TESTE
# ===============================
# Instância do Flask para o Webhook
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
# INICIALIZAÇÃO PRINCIPAL DO SERVIDOR E BOT
# ===============================
async def main():
    """Inicializa o servidor Flask e a busca de arbitragem."""
    
    # Inicia os handlers do bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))

    # Inicia a busca de arbitragem simulada em uma tarefa assíncrona em background
    asyncio.create_task(find_and_alert_arbitrage_loop_simulated())
    
    # Inicia a aplicação do Telegram (necessário para o processamento do webhook)
    await application.initialize()

    # Inicia o servidor Flask para escutar o webhook
    print("🚀 Bot de Arbitragem (SIMULAÇÃO) rodando via Webhook no Railway! Servidor Flask ativo.")
    # flask_run_args = {
    #     "host": "0.0.0.0",
    #     "port": int(os.environ.get("PORT", 8080))
    # }
    # await app_flask.run(**flask_run_args)
    # A função abaixo irá iniciar o servidor web e o loop de eventos para o bot
    # conforme a documentação do python-telegram-bot
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path="/webhook"
    )

if __name__ == '__main__':
    # Esta é a forma correta de iniciar a aplicação assíncrona principal.
    asyncio.run(main())
