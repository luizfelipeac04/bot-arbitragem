import requests
import asyncio
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7841837460:AAH_ImNJbNfbJZWy7MymGJ7fMiRTqdO9dM0'
API_KEY = '39dd66405e32c31d2ae04fafe6b31579'
REGION = 'all'
SPORT = 'soccer'

BOOKMAKERS = {
    'Bet365': 'https://www.bet365.com/',
    'Betfair': 'https://www.betfair.com/',
    'Pinnacle': 'https://www.pinnacle.com/',
    'Unibet': 'https://www.unibet.com/',
    'Matchbook': 'https://www.matchbook.com/',
    'Betano': 'https://www.betano.com/',
    '1xBet': 'https://1xbet.com/',
    'Sportingbet': 'https://www.sportingbet.com/',
    'Bodog': 'https://www.bodog.com/',
    'Betway': 'https://www.betway.com/'
}

usuarios_ativos = {}
jogos_alertados = set()
MERCADOS_SUPORTADOS = ['h2h', 'totals']

def calcular_apostas(odds, total):
    inversos = [1 / odd for odd in odds]
    soma_inversos = sum(inversos)
    apostas = [(inv / soma_inversos) * total for inv in inversos]
    retornos = [apostas[i] * odds[i] for i in range(len(odds))]
    lucro = min(retornos) - total
    return apostas, lucro

async def buscar_oportunidades(app):
    print("🔍 Monitorando arbitragem...")
    while True:
        try:
            url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
            params = {
                'apiKey': API_KEY,
                'regions': REGION,
                'markets': ','.join(MERCADOS_SUPORTADOS),
                'oddsFormat': 'decimal'
            }
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Erro API: {response.status_code}, {response.text}")
                await asyncio.sleep(60)
                continue

            jogos = response.json()
            print(f"🎯 Analisando {len(jogos)} jogos...")

            for jogo in jogos:
                jogo_id = f"{jogo['home_team']} x {jogo['away_team']} - {jogo['commence_time']}"
                if jogo_id in jogos_alertados:
                    continue

                oportunidades = []

                for market_type in MERCADOS_SUPORTADOS:
                    odds_map = {}
                    for site in jogo.get('bookmakers', []):
                        nome = site['title']
                        link = BOOKMAKERS.get(nome, '')
                        for market in site.get('markets', []):
                            if market['key'] != market_type:
                                continue
                            for outcome in market['outcomes']:
                                nome_opcao = outcome['name']
                                if nome_opcao not in odds_map:
                                    odds_map[nome_opcao] = []
                                odds_map[nome_opcao].append((outcome['price'], nome, link))

                    if len(odds_map) >= 2:
                        melhores = []
                        for opcao, lista in odds_map.items():
                            melhor = max(lista, key=lambda x: x[0])
                            melhores.append((opcao, *melhor))

                        odds = [item[1] for item in melhores]
                        casas = [(item[2], item[3]) for item in melhores]

                        if len(odds) >= 2:
                            inv = sum(1 / o for o in odds)
                            if inv < 1:
                                lucro_pct = round((1 - inv) * 100, 2)
                                oportunidades.append((market_type, melhores, lucro_pct))

                if oportunidades:
                    for market_type, melhores, lucro_pct in oportunidades:
                        msg = f"💰 *Arbitragem Detectada!*\n🏟️ *{jogo['home_team']} x {jogo['away_team']}*\n🕒 *Data:* {jogo['commence_time'].replace('T',' ').replace('Z','')}\n🎯 *Mercado:* {'Resultado Final' if market_type == 'h2h' else 'Mais/Menos Gols'}\n📈 *Lucro Estimado:* {lucro_pct:.2f}%\n\nDigite o valor que deseja apostar para ver o cálculo."

                        for user_id in usuarios_ativos:
                            await app.bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.MARKDOWN)
                            odds = [x[1] for x in melhores]
                            casas = [(x[2], x[3]) for x in melhores]
                            usuarios_ativos[user_id] = (jogo_id, odds, casas)

                    jogos_alertados.add(jogo_id)

        except Exception as e:
            print(f"Erro: {e}")
        await asyncio.sleep(60)

async def tratar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    texto = update.message.text.strip()

    if user_id in usuarios_ativos:
        try:
            valor = float(texto)
            jogo_id, odds, casas = usuarios_ativos[user_id]
            apostas, lucro = calcular_apostas(odds, valor)
            lucro_pct = (lucro / valor) * 100

            msg = f"📊 *Cálculo para R${valor:.2f}*\n"
            for i, (odd, (casa, link)) in enumerate(zip(odds, casas)):
                msg += f"🔸 Aposte R${apostas[i]:.2f} na [{casa}]({link}) (Odd: {odd})\n"

            msg += f"\n💵 *Lucro Estimado:* R${lucro:.2f} ({lucro_pct:.2f}%)"
            await context.bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except:
            await context.bot.send_message(chat_id=user_id, text="❌ Valor inválido. Envie só números, ex: 500")
    else:
        await context.bot.send_message(chat_id=user_id, text="👋 Envie um valor quando receber uma arbitragem.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), tratar_mensagem))
    asyncio.create_task(buscar_oportunidades(app))
    print("🤖 Bot rodando...")
    await app.run_polling()

# 🟢 Correção para Windows (event loop)
if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
