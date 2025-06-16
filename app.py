from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import time
import requests 

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDS_API_KEY") 

SPORT = 'soccer' 
REGION = 'us,eu,uk,au' 
MARKETS = 'h2h' 
BOOKMAKERS_LIMIT = 5 
MIN_PROFIT_PERCENT = 1.0 
SEARCH_INTERVAL_SECONDS = 120 # Manter para simulação interna, sem loop automático

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
    'Betcris': 'https://www.kto.com/',
}

alerted_opportunities = set()

# Instância global do Bot e Application
# Não inicializamos aqui, a inicialização será feita dentro de run_bot_polling_main_simple()
application = None 

# ===============================
# FUNÇÕES DE CÁLCULO DE ARBITRAGEM
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
# FUNÇÕES DO BOT TELEGRAM (Polling)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start."""
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE via Polling! Use /status para checar, e /buscar_simulado para ver uma arbitragem.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica o status do bot."""
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

async def buscar_simulado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para simular uma busca de arbitragem e enviar um alerta."""
    await update.message.reply_text("🔍 Buscando oportunidades de arbitragem (simulação)...")
    await asyncio.sleep(2) # Simula um delay na busca
    
    # Exemplo de oportunidade simulada
    simulated_game_id_counter = len(alerted_opportunities) + 1
    game_id_unique = f"SIM-{simulated_game_id_counter}-{time.time()}"

    game_simulado = {
        'id': game_id_unique,
        'home_team': f'Time Simulado A {simulated_game_id_counter}',
        'away_team': f'Time Simulado B {simulated_game_id_counter}',
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
    
    message = format_arbitrage_message(game_simulado, best_odds_info_simulado, profit_simulado)
    
    if CHAT_ID:
        await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
        print(f"✅ Alerta de arbitragem SIMULADA enviado via comando! Lucro: {profit_simulado:.2f}%")
    else:
        print(f"Alerta de arbitragem SIMULADA encontrado, mas CHAT_ID não configurado. Lucro: {profit_simulado:.2f}%")

# ===============================
# INICIALIZAÇÃO PRINCIPAL (Polling)
# ===============================
def run_bot_polling_main_simple():
    """Função principal que configura e roda o bot."""
    global application # Acessa a variável global application
    application = Application.builder().token(TOKEN).build() # Inicializa o Application aqui

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("buscar_simulado", buscar_simulado)) 
    
    print("🚀 Bot rodando via Polling no Railway (versão estável inicial - SIMPLIFICADA)!")
    
    # Inicia o modo polling. Este método é bloqueante e gerencia
    # o loop de eventos principal para o bot.
    # O Railway deve conseguir executar isso como o processo principal.
    application.run_polling(poll_interval=1.0) 

if __name__ == '__main__':
    # Chamada direta da função principal.
    # Sem asyncio.run() explícito, sem threads, sem APScheduler.
    # Deixa o Railway rodar esta função como o processo principal.
    run_bot_polling_main_simple()
