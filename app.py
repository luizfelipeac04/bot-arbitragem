from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio
import time
import requests
from flask import Flask, request # Importar Flask para o Webhook

# ===============================
# CONFIGURAÇÕES DO BOT
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDS_API_KEY") 

# CORREÇÃO AQUI: Apenas um esporte para compatibilidade com a API de testes e evitar 404
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

# Instância global do Application para o Webhook
application = Application.builder().token(TOKEN).build()
# Instância do Flask para o Webhook
app_flask = Flask(__name__)

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
# FUNÇÕES DO BOT TELEGRAM (para Webhook)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot de Arbitragem está ONLINE e buscando oportunidades automaticamente (via Webhook)! Use /status para checar.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ O bot está funcionando corretamente e buscando oportunidades a cada {SEARCH_INTERVAL_SECONDS / 60:.0f} minutos.")

# Registra os handlers no aplicativo global
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

# ===============================
# LÓGICA PRINCIPAL DE BUSCA DE ARBITRAGEM (AUTOMÁTICA)
# ===============================
async def find_and_alert_arbitrage_loop():
    """
    Loop contínuo para buscar por oportunidades de arbitragem e enviar alertas.
    Esta função é agendada para rodar em segundo plano pelo Webhook.
    """
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
                            await application.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown', disable_web_page_preview=True)
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
# ROTAS DO FLASK PARA O WEBHOOK E TESTE
# ===============================
@app_flask.route('/webhook', methods=['POST'])
async def webhook():
    """Rota que o Telegram envia as atualizações."""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update) # Processa a atualização do Telegram
        return "ok"
    return "Webhook running!"

@app_flask.route('/')
def home():
    """Rota de teste para verificar se o servidor está ativo."""
    return "🚀 Bot de Arbitragem está rodando com Webhook no Railway! Servidor Flask OK."

# ===============================
# INICIALIZAÇÃO PRINCIPAL
# ===============================
async def run_server_and_bot():
    """Inicializa o servidor Flask e a busca de arbitragem."""
    
    # Inicia a busca de arbitragem em uma tarefa assíncrona separada
    asyncio.create_task(find_and_alert_arbitrage_loop())

    # Inicia o servidor Flask para escutar o webhook
    # railway_static_url = os.environ.get('RAILWAY_STATIC_URL', 'your-railway-domain.up.railway.app')
    # print(f"Configurando webhook para: https://{railway_static_url}/webhook")
    
    # A Application.run_webhook já gerencia o servidor Flask e o processamento de updates
    # Não é necessário app_flask.run() aqui diretamente.
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path="/webhook"
        # O webhook_url é definido externamente via API do Telegram.
    )

if __name__ == '__main__':
    # Inicializa o Application do bot antes de tudo
    asyncio.run(application.initialize()) # Garante que o bot seja inicializado

    # Roda a função principal assíncrona
    asyncio.run(run_server_and_bot())
