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
API_KEY = os.getenv("ODDS_API_KEY") # Chave da The Odds API real
# ATENÇÃO: Se seus créditos estiverem esgotados ou a chave for inválida, isso gerará um erro 401 ou 403.

SPORT = 'soccer' # Apenas um esporte para evitar erro 404 e consumo excessivo de créditos no plano free
REGION = 'us,eu,uk,au' 
MARKETS = 'h2h' 
BOOKMAKERS_LIMIT = 5 
MIN_PROFIT_PERCENT = 1.0 # Filtrar por lucro mínimo de 1%

# SEARCH_INTERVAL_SECONDS não será usado para loop automático, apenas para referência
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
    'Betcris': 'https://www.kto.com/',
}

alerted_opportunities = set()

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
    commence_time_str = game['commence_time'].replace('T', ' ').replace('Z', '')[:16]

    sport_name = game.get('sport_title', 'Esporte Desconhecido') 

    message = (
        f"💰 *Arbitragem Encontrada!* \n\n"
        f"⚽️ *Jogo:* {home_team} vs {away_team}\n"
        f"📅 *Data:* {commence_time_str}\n"
        f"🏆 *Esporte:* {sport_name}\n" 
        f"📈 *Lucro Garantido:* {profit_percent:.2f}%\n\n"
        f"🔹 *Onde Apostar:*\n"
    )

    for outcome_name, odd_data in best_odds_info.items():
        odd = odd_data['odd']
        bookmaker = odd_data['bookmaker']
        link = BOOKMAKERS_LINKS.get(bookmaker, f"https://www.google.com/search?q={bookmaker}")
        
        label = outcome_name
        if outcome_name == 'home':
            label = '🏠 Mandante'
        elif outcome_name == 'draw':
            label = '🤝 Empate'
        elif outcome_name == 'away':
            label = '🏃 Visitante'
            
        message += f"{label}: *{odd:.2f}* na [{bookmaker}]({link})\n"
        
    return message

# ===============================
# FUNÇÕES DO BOT TELEGRAM (Polling)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde ao comando /start."""
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE via Polling! Use /status para checar, e /buscar_real para procurar uma arbitragem.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica o status do bot."""
    await update.message.reply_text("✅ O bot está funcionando corretamente!")

async def buscar_real(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para buscar arbitragem real na API."""
    await update.message.reply_text("🔍 Buscando oportunidades de arbitragem REAL... aguarde por alertas!")
    await asyncio.sleep(2) # Simula um delay na busca
    
    # --- LÓGICA DE BUSCA REAL (CHAMA A API EXTERNA) ---
    try:
        url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
        
        response = requests.get(url)
        response.raise_for_status() # Lança um erro para status de resposta HTTP ruins (4xx ou 5xx)
        data = response.json()
        
        print(f"🎯 Analisando {len(data)} jogos para arbitragem (API REAL)...")

        if not data:
            print("Nenhum jogo encontrado na API ou API retornou vazio.")
            await update.message.reply_text("ℹ️ Nenhuma oportunidade encontrada na busca real no momento.")
            return

        for game in data:
            game_id_unique = f"{game['id']}-{game['commence_time']}"
            
            if game_id_unique in alerted_opportunities:
                continue 

            best_odds_for_outcomes = {}

            for bookmaker_data in game['bookmakers']:
                bookmaker_name = bookmaker_data['title']
                
                for market in bookmaker_data['markets']:
                    if market['key'] == MARKETS:
                        for outcome in market['outcomes']:
                            outcome_name = outcome['name'].lower()
                            outcome_price = outcome['price']

                            if outcome_name not in best_odds_for_outcomes or outcome_price > best_odds_for_outcomes[outcome_name]['odd']:
                                best_odds_for_outcomes[outcome_name] = {
                                    'odd': outcome_price,
                                    'bookmaker': bookmaker_name
                                }
            
            if len(best_odds_for_outcomes) == 3 and all(key in best_odds_for_outcomes for key in ['home', 'draw', 'away']):
                
                odds_list = [best_odds_for_outcomes['home']['odd'], 
                             best_odds_for_outcomes['draw']['odd'], 
                             best_odds_for_outcomes['away']['odd']]
                
                profit = calculate_arbitrage_profit(odds_list)

                if profit >= MIN_PROFIT_PERCENT:
                    message = format_arbitrage_message(game, best_odds_for_outcomes, profit)
                    
                    if CHAT_ID:
                        await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)
                        alerted_opportunities.add(game_id_unique)
                        print(f"✅ Alerta de arbitragem REAL enviado! Lucro: {profit:.2f}%")
                    else:
                        print(f"Alerta de arbitragem REAL encontrado, mas CHAT_ID não configurado. Lucro: {profit:.2f}%")
                else:
                    print(f"Oportunidade de arbitragem REAL encontrada, mas lucro ({profit:.2f}%) abaixo do mínimo ({MIN_PROFIT_PERCENT}%)")
            else:
                print(f"Não há odds completas (home/draw/away) para o jogo {game.get('home_team')} vs {game.get('away_team')}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição à API de Odds: {e}")
        # Se for erro 401 ou 403, avisa o usuário no Telegram
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code in [401, 403]:
            await update.message.reply_text("ATENÇÃO: Sua API Key da The Odds API está inválida ou sem créditos. Verifique sua conta!")
        else:
            await update.message.reply_text(f"❌ Erro ao buscar oportunidades na API: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado na busca de arbitragem REAL: {e}")
        await update.message.reply_text(f"❌ Erro inesperado: {e}")

# ===============================
# INICIALIZAÇÃO PRINCIPAL (Polling)
# ===============================
def run_bot_polling_main_simple():
    """Função principal que configura e roda o bot."""
    global application 
    application = Application.builder().token(TOKEN).build() 

    # Adiciona os handlers para os comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("buscar_real", buscar_real)) # Comando para buscar REAL
    
    print("🚀 Bot rodando via Polling no Railway (versão com API REAL - MANUAL)!")
    
    # Inicia o modo polling (o bot escuta por atualizações do Telegram)
    application.run_polling(poll_interval=1.0) 

if __name__ == '__main__':
    # Chamada direta da função principal.
    # Sem asyncio.run() explícito, sem threads, sem APScheduler.
    # Deixa o Railway rodar esta função como o processo principal.
    run_bot_polling_main_simple()
