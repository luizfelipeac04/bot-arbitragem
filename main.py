import os
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ArbitrageBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.odds_api_key = os.getenv('THE_ODDS_API_KEY')
        self.odds_api_url = "https://api.the-odds-api.com/v4"
        self.min_profit_margin = 1.0  # 1% mínimo
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        keyboard = [
            [InlineKeyboardButton("🔍 Buscar Arbitragens", callback_data='search_arb')],
            [InlineKeyboardButton("⚙️ Configurações", callback_data='settings')],
            [InlineKeyboardButton("📊 Esportes Disponíveis", callback_data='sports')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_msg = """
🤖 *Bot de Arbitragem de Apostas*

Bem-vindo! Este bot encontra oportunidades de arbitragem com retorno garantido mínimo de 1%.

*Funcionalidades:*
• Análise em tempo real das odds
• Cálculo automático de lucro
• Sugestão de valores para apostar
• Alertas de oportunidades

Use os botões abaixo para começar!
        """
        
        await update.message.reply_text(
            welcome_msg, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    def get_sports(self) -> List[Dict]:
        """Busca esportes disponíveis na API"""
        try:
            url = f"{self.odds_api_url}/sports"
            params = {
                'apiKey': self.odds_api_key,
                'all': 'false'  # Apenas esportes ativos
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao buscar esportes: {e}")
            return []

    def get_odds(self, sport_key: str) -> List[Dict]:
        """Busca odds para um esporte específico"""
        try:
            url = f"{self.odds_api_url}/sports/{sport_key}/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us,uk,eu',  # Múltiplas regiões para mais casas
                'markets': 'h2h',  # Head to head (1x2 ou moneyline)
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao buscar odds para {sport_key}: {e}")
            return []

    def calculate_arbitrage(self, odds_data: List[Dict]) -> List[Dict]:
        """Calcula oportunidades de arbitragem"""
        arbitrage_opportunities = []
        
        for game in odds_data:
            try:
                bookmakers = game.get('bookmakers', [])
                if len(bookmakers) < 2:
                    continue
                
                # Organizar odds por resultado
                outcomes = {}
                for bookmaker in bookmakers:
                    bookie_name = bookmaker['title']
                    markets = bookmaker.get('markets', [])
                    
                    for market in markets:
                        if market['key'] != 'h2h':
                            continue
                            
                        for outcome in market['outcomes']:
                            outcome_name = outcome['name']
                            price = float(outcome['price'])
                            
                            if outcome_name not in outcomes:
                                outcomes[outcome_name] = []
                            
                            outcomes[outcome_name].append({
                                'bookmaker': bookie_name,
                                'odds': price
                            })
                
                # Encontrar melhores odds para cada resultado
                if len(outcomes) < 2:
                    continue
                
                best_odds = {}
                for outcome_name, odds_list in outcomes.items():
                    best_odd = max(odds_list, key=lambda x: x['odds'])
                    best_odds[outcome_name] = best_odd
                
                # Calcular se há arbitragem
                implied_probabilities = []
                total_investment = 100  # Base de R$ 100
                
                for outcome_name, best_odd in best_odds.items():
                    implied_prob = 1 / best_odd['odds']
                    implied_probabilities.append(implied_prob)
                
                total_implied_prob = sum(implied_probabilities)
                
                if total_implied_prob < 1.0:  # Há oportunidade de arbitragem
                    profit_margin = ((1 / total_implied_prob) - 1) * 100
                    
                    if profit_margin >= self.min_profit_margin:
                        # Calcular distribuição de apostas
                        stakes = {}
                        for outcome_name, best_odd in best_odds.items():
                            stake_percentage = (1 / best_odd['odds']) / total_implied_prob
                            stake_amount = total_investment * stake_percentage
                            stakes[outcome_name] = {
                                'bookmaker': best_odd['bookmaker'],
                                'odds': best_odd['odds'],
                                'stake': round(stake_amount, 2),
                                'potential_return': round(stake_amount * best_odd['odds'], 2)
                            }
                        
                        arbitrage_opportunities.append({
                            'game': f"{game.get('home_team', 'Casa')} vs {game.get('away_team', 'Visitante')}",
                            'sport': game.get('sport_title', 'Desconhecido'),
                            'commence_time': game.get('commence_time', ''),
                            'profit_margin': round(profit_margin, 2),
                            'total_stake': total_investment,
                            'guaranteed_profit': round(total_investment * (profit_margin / 100), 2),
                            'bets': stakes
                        })
                        
            except Exception as e:
                logger.error(f"Erro ao calcular arbitragem: {e}")
                continue
        
        # Ordenar por margem de lucro
        arbitrage_opportunities.sort(key=lambda x: x['profit_margin'], reverse=True)
        return arbitrage_opportunities

    async def search_arbitrage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Busca oportunidades de arbitragem"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text("🔍 Buscando oportunidades de arbitragem...")
        
        # Buscar esportes principais
        main_sports = ['soccer', 'basketball', 'tennis', 'americanfootball_nfl']
        all_opportunities = []
        
        for sport in main_sports:
            try:
                odds_data = self.get_odds(sport)
                if odds_data:
                    opportunities = self.calculate_arbitrage(odds_data)
                    all_opportunities.extend(opportunities)
            except Exception as e:
                logger.error(f"Erro ao processar {sport}: {e}")
        
        if not all_opportunities:
            await query.edit_message_text(
                "❌ Nenhuma oportunidade de arbitragem encontrada no momento.\n"
                "Tente novamente em alguns minutos."
            )
            return
        
        # Mostrar top 5 oportunidades
        message = "🎯 *Melhores Oportunidades de Arbitragem*\n\n"
        
        for i, opp in enumerate(all_opportunities[:5], 1):
            message += f"*{i}. {opp['game']}*\n"
            message += f"🏆 Esporte: {opp['sport']}\n"
            message += f"💰 Lucro: {opp['profit_margin']:.2f}% ({opp['guaranteed_profit']:.2f})\n"
            message += f"💵 Investimento: R$ {opp['total_stake']:.2f}\n\n"
            
            for outcome, bet_info in opp['bets'].items():
                message += f"  • {outcome}: R$ {bet_info['stake']:.2f} "
                message += f"@{bet_info['odds']:.2f} ({bet_info['bookmaker']})\n"
            
            message += "\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Atualizar", callback_data='search_arb')],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def show_sports(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra esportes disponíveis"""
        query = update.callback_query
        await query.answer()
        
        sports = self.get_sports()
        
        if not sports:
            await query.edit_message_text("❌ Erro ao carregar esportes disponíveis.")
            return
        
        message = "📊 *Esportes Disponíveis para Arbitragem*\n\n"
        
        for sport in sports[:10]:  # Mostrar apenas os primeiros 10
            message += f"• {sport.get('title', 'N/A')} ({sport.get('key', 'N/A')})\n"
        
        keyboard = [
            [InlineKeyboardButton("🔍 Buscar Arbitragens", callback_data='search_arb')],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra configurações"""
        query = update.callback_query
        await query.answer()
        
        message = f"""
⚙️ *Configurações do Bot*

• Margem mínima de lucro: {self.min_profit_margin}%
• Regiões das casas: US, UK, EU
• Mercados: Head-to-Head (1x2)
• Formato das odds: Decimal
• Atualização: Manual

*Status da API:* ✅ Conectada
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Buscar Arbitragens", callback_data='search_arb')],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Volta ao menu principal"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("🔍 Buscar Arbitragens", callback_data='search_arb')],
            [InlineKeyboardButton("⚙️ Configurações", callback_data='settings')],
            [InlineKeyboardButton("📊 Esportes Disponíveis", callback_data='sports')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_msg = """
🤖 *Bot de Arbitragem de Apostas*

Bot ativo e pronto para encontrar oportunidades!

*Status:*
• ✅ API The-Odds conectada
• ✅ Análise em tempo real
• ✅ Cálculos de lucro otimizados

Use os botões abaixo:
        """
        
        await query.edit_message_text(
            welcome_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para botões inline"""
        query = update.callback_query
        
        handlers = {
            'search_arb': self.search_arbitrage,
            'sports': self.show_sports,
            'settings': self.show_settings,
            'main_menu': self.main_menu
        }
        
        handler = handlers.get(query.data)
        if handler:
            await handler(update, context)

    def run(self):
        """Inicia o bot"""
        if not self.telegram_token:
            logger.error("Token do Telegram não encontrado!")
            return
        
        if not self.odds_api_key:
            logger.error("API Key do The-Odds não encontrada!")
            return
        
        # Criar aplicação
        application = Application.builder().token(self.telegram_token).build()
        
        # Registrar handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Iniciar bot
        logger.info("Bot iniciado!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = ArbitrageBot()
    bot.run()
