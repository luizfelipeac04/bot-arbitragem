import requests
import asyncio
import nest_asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Corrigir event loop duplicado (problema comum na Render com polling)
nest_asyncio.apply()

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7841837460:AAH_ImNJbNfbJZWy7MymGJ7fMiRTqdO9dM0'
API_KEY = '39dd66405e32c31d2ae04fafe6b31579'
SPORT = 'soccer'
REGION = 'all'  # Usar todas as regiões suportadas
MARKET = 'h2h'  # Mercado head-to-head (resultado final)
BOOKMAKERS = ''  # Deixe vazio para usar todas as casas disponíveis
ARBITRAGE_THRESHOLD = 0.98  # 2% de lucro
CHECK_INTERVAL = 60  # segundos

# Armazena dados temporários
arbitrage_cache = {}

# === FUNÇÕES AUXILIARES ===
def calcular_apostas(odds, investimento_total):
    prob_invertidas = [1/o for o in odds]
    soma = sum(prob_invertidas)
    apostas = [(1/o)/soma * investimento_total for o in odds]
    lucro_estimado = min([a * o for a, o in zip(apostas, odds)]) - investimento_total
    return apostas, lucro_estimado

def formatar_mensagem_arbitragem(jogo, investimento_total):
    teams = jogo['teams']
    commence_time = jogo['commence_time']
    sites = jogo['bookmakers']

    odds_melhores = [0, 0, 0]
    casas = ['', '', '']
    links = ['', '', '']

    for site in sites:
        outcomes = site['markets'][0]['outcomes']
        for i, outcome in enumerate(outcomes):
            if outcome['price'] > odds_melhores[i]:
                odds_melhores[i] = outcome['price']
                casas[i] = site['title']
                links[i] = gerar_link_casa(site['title'])

    apostas, lucro = calcular_apostas(odds_melhores, investimento_total)

    mensagem = f"""
💰 <b>Arbitragem Encontrada!</b>

🏟️ <b>Jogo:</b> {teams[0]} vs {teams[1]}
📅 <b>Data:</b> {commence_time}
📈 <b>Lucro Estimado:</b> {lucro:.2f}
💸 <b>Investimento:</b> R$ {investimento_total:.2f}

<b>Onde Apostar:</b>
🏠 {teams[0]}: <b>{odds_melhores[0]}</b> na <a href='{links[0]}'>{casas[0]}</a> → R$ {apostas[0]:.2f}
🤝 Empate: <b>{odds_melhores[1]}</b> na <a href='{links[1]}'>{casas[1]}</a> → R$ {apostas[1]:.2f}
🏃 {teams[1]}: <b>{odds_melhores[2]}</b> na <a href='{links[2]}'>{casas[2]}</a> → R$ {apostas[2]:.2f}
"""
    return mensagem

def gerar_link_casa(nome):
    links = {
        "Betfair": "https://www.betfair.com/",
        "1xBet": "https://1xbet.com/",
        "Bet365": "https://www.bet365.com/",
        "Pinnacle": "https://www.pinnacle.com/",
        "William Hill": "https://www.williamhill.com/",
        "Bovada": "https://www.bovada.lv/"
    }
    return links.get(nome, 'https://www.google.com/search?q=' + nome)

async def verificar_arbitragem(bot):
    print("🔍 Monitorando arbitragem...")
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds?apiKey={API_KEY}&regions={REGION}&markets={MARKET}&oddsFormat=decimal"

    while True:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("❌ Erro na API:", response.status_code, response.text)
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            data = response.json()
            print(f"🎯 Analisando {len(data)} jogos...")

            for jogo in data:
                if jogo['id'] in arbitrage_cache:
                    continue

                melhores_odds = [0, 0, 0]
                for site in jogo['bookmakers']:
                    for i, outcome in enumerate(site['markets'][0]['outcomes']):
                        if outcome['price'] > melhores_odds[i]:
                            melhores_odds[i] = outcome['price']

                if 0 in melhores_odds:
                    continue

                soma_prob = sum([1/o for o in melhores_odds])
                if soma_prob < ARBITRAGE_THRESHOLD:
                    arbitrage_cache[jogo['id']] = True
                    mensagem = formatar_mensagem_arbitragem(jogo, investimento_total=100)
                    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=mensagem, parse_mode=ParseMode.HTML)

        except Exception as e:
            print("Erro:", str(e))

        await asyncio.sleep(CHECK_INTERVAL)

# === HANDLER PARA MENSAGENS ===
ADMIN_CHAT_ID = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = update.effective_chat.id
    await update.message.reply_text("🤖 Bot de Arbitragem ativado! Aguarde por oportunidades.")

# === FUNÇÃO PRINCIPAL ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))
    asyncio.create_task(verificar_arbitragem(app.bot))
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
