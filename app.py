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
REGION = 'all' 
MARKETS = 'h2h' 
BOOKMAKERS_LIMIT = 5 
MIN_PROFIT_PERCENT = 1.0 
SEARCH_INTERVAL_SECONDS = 120 

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

    message = (
        f"💰 *Arbitragem Encontrada!* \n\n"
        f"⚽️ *Jogo:* {home_team} vs {away_team}\n"
        f"📅 *Data:* {commence_time_str}\n"
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
# FUNÇÕES DO BOT TELEGRAM
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE e buscando oportunidades automaticamente! Use /status para checar.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O bot está funcionando corretamente e buscando oportunidades a cada 2 minutos.")

# ===============================
# LÓGICA PRINCIPAL DE BUSCA DE ARBITRAGEM (AUTOMÁTICA)
# ===============================
async def find_and_alert_arbitrage_loop(app_bot: Application):
    while True:
        print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Seu bot está procurando oportunidades, aguarde...") 
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}&oddsFormat=decimal"
            
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()
            
            print(f"🎯 Analisando {len(data)} jogos para arbitragem...")

            if not data:
                print("Nenhum jogo encontrado ou API retornou vazio.")
                
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
                            await app_bot.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
                            alerted_opportunities.add(game_id_unique)
                            print(f"✅ Alerta de arbitragem enviado! Lucro: {profit:.2f}%")
                        else:
                            print(f"Alerta de arbitragem encontrado, mas CHAT_ID não configurado. Lucro: {profit:.2f}%")
                    else:
                        print(f"Oportunidade de arbitragem encontrada, mas lucro ({profit:.2f}%) abaixo do mínimo ({MIN_PROFIT_PERCENT}%)")
                else:
                    print(f"Não há odds completas (home/draw/away) para o jogo {game.get('home_team')} vs {game.get('away_team')}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição à API de Odds: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado na busca de arbitragem: {e}")
        
        await asyncio.sleep(SEARCH_INTERVAL_SECONDS) 

# ===============================
# INICIALIZANDO O BOT (Polling)
# ===============================
async def main_bot_runner():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    
    print("🚀 Bot rodando via Polling no Railway!")
    
    asyncio.create_task(find_and_alert_arbitrage_loop(application))
    
    await application.run_polling(poll_interval=1.0) 

if __name__ == '__main__':
    # O Railway já inicia um loop de eventos principal para o processo.
    # Chamamos a função diretamente para que ela rode dentro desse loop.
    asyncio.run(main_bot_runner()) # Correção aplicada aqui
