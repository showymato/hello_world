"""
Configuration for Professional Crypto Analysis Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class AnalysisConfig:
    # Telegram Configuration (ONLY thing user needs to set)
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

    # Trading Pairs to Analyze
    SYMBOLS = ['ETH/USDT', 'BTC/USDT', 'SOL/USDT']
    DEFAULT_SYMBOL = 'ETH/USDT'

    # Analysis Timeframes
    INTRADAY_TIMEFRAMES = ['15m', '1h']
    SWING_TIMEFRAMES = ['4h', '1d']

    # Technical Analysis Settings
    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9

    # Risk Management
    MAX_RISK_PER_TRADE = 2.0  # 2% maximum risk
    INTRADAY_LEVERAGE = 5
    SWING_LEVERAGE = 3

    # Report Settings
    ANALYSIS_INTERVAL = 60  # Generate report every 60 minutes
    TIMEZONE = 'UTC'

    # Exchange Settings
    EXCHANGE = 'binance'

    # Deployment Settings
    PORT = int(os.getenv('PORT', 8000))
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://your-app.onrender.com')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
