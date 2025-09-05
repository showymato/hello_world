"""
Professional-grade data fetcher for crypto analysis
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self, exchange_name='binance'):
        self.exchange = getattr(ccxt, exchange_name)({
            'sandbox': False,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    async def get_market_data(self, symbol: str, timeframes: list, limit: int = 200) -> dict:
        """Fetch market data for multiple timeframes"""
        try:
            market_data = {}

            for timeframe in timeframes:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                market_data[timeframe] = df

            logger.info(f"Fetched data for {symbol} across {len(timeframes)} timeframes")
            return market_data

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {}

    def get_current_price(self, symbol: str) -> dict:
        """Get current market price and 24h stats"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['baseVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low']
            }
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            return {}

    def get_anchor_candle(self, df: pd.DataFrame) -> dict:
        """Get the most recent completed candle as anchor"""
        try:
            latest = df.iloc[-2]  # Use -2 to get completed candle
            return {
                'timestamp': latest.name,
                'open': latest['open'],
                'high': latest['high'], 
                'low': latest['low'],
                'close': latest['close'],
                'volume': latest['volume']
            }
        except Exception as e:
            logger.error(f"Error getting anchor candle: {e}")
            return {}
