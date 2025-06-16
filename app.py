from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import time
import requests # Ainda importamos, mas não usaremos requests.get diretamente na simulação

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDS_API_KEY") # Manter a variável, mas não será usada na simulação

SPORT = 'soccer' # Apenas um esporte para consistência, mas não usado na simulação
REGION = 'us,eu,uk,au' # Não usado na simulação
MARKETS = 'h2h' # Não usado na simulação
BOOKMAKERS_LIMIT = 5 # Não usado na simulação
MIN_PROFIT_PERCENT = 1.0 # Usado na simulação para formatar a mensagem fictícia
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
# FUNÇÕES DO BOT TELEGRAM
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem (Simulação) está ONLINE e buscando oportunidades automaticamente! Use /status para checar.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ O bot está funcionando corretamente e buscando oportunidades a cada {SEARCH_INTERVAL_SECONDS / 60:.0f} minutos (Simulação).")

# ===============================
# LÓGICA PRINCIPAL DE BUSCA DE ARBITRAGEM (SIMULADA INTERNAMENTE)
# ===============================
async def find_and_alert_arbitrage_loop(app_bot: Application):
    simulated_game_id_counter = 0 # Contador para IDs de jogos simulados

    while True:
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Seu bot está PROCURANDO OPORTUNIDADES (SIMULAÇÃO), aguarde...") 
        try:
            # --- LÓGICA DE SIMULAÇÃO (NÃO CHAMA API EXTERNA) ---
            simulated_game_id_counter += 1
            game_id_unique = f"SIM-{simulated_game_id_counter}-{time.time()}"
            
            # Gerar uma arbitragem simulada a cada X ciclos (ex: a cada 2 ciclos para testar)
            # Ou sempre gerar, para ver a mensagem
            
            # Simulação de dados de uma arbitragem
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
            
            profit_simulado = calculate_arbitrage_profit(odds_list_simulado) # Calcula o lucro simulado
            
            # --- FIM DA LÓGICA DE SIMULAÇÃO ---

            if game_id_unique in alerted_opportunities:
                print("Oportunidade simulada já alertada. Pulando.")
                await asyncio.sleep(SEARCH_INTERVAL_SECONDS) # Ainda espera para o próximo ciclo
                continue 
            
            if profit_simulado >= MIN_PROFIT_PERCENT:
                message = format_arbitrage_message(game_simulado, best_odds_info_simulado, profit_simulado)
                
                if CHAT_ID:
                    await app_bot.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
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
# INICIALIZAÇÃO PRINCIPAL (Polling)
# ===============================
async def run_bot_polling_main():
    """Inicializa o bot e o loop de polling."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    
    print("🚀 Bot de Arbitragem (SIMULAÇÃO) rodando via Polling no Railway!")
    
    # Cria a tarefa de busca em background (agora simulada).
    asyncio.create_task(find_and_alert_arbitrage_loop(application))
    
    # Inicia o polling.
    await application.run_polling(poll_interval=1.0) 

if __name__ == '__main__':
    asyncio.run(run_bot_polling_main())
