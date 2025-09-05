"""
Enhanced multi-source data fetcher with Binance + Bybit + CoinGecko integration
"""
import ccxt
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
import logging
import requests

logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self, exchange_name='binance'):
        # Primary exchange (Binance) - your existing setup
        self.exchange = getattr(ccxt, exchange_name)({
            'sandbox': False,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Backup exchange (Bybit) - NEW
        try:
            self.backup_exchange = ccxt.bybit({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
        except:
            self.backup_exchange = None
        
        # CoinGecko for market context - NEW
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
    async def get_market_data(self, symbol: str, timeframes: list, limit: int = 200) -> dict:
        """Enhanced market data with fallback sources"""
        try:
            # Try primary source (Binance) first
            market_data = await self._fetch_primary(symbol, timeframes, limit)
            
            # If primary fails, try backup
            if not market_data and self.backup_exchange:
                logger.warning("🔄 Primary failed, trying Bybit backup...")
                market_data = await self._fetch_backup(symbol, timeframes, limit)
            
            # Add market context from CoinGecko
            if market_data:
                context = await self._get_market_context(symbol)
                market_data['market_context'] = context
                logger.info(f"✅ Enhanced data fetched for {symbol} with market context")
            
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Enhanced data fetch error: {e}")
            return {}
    
    async def _fetch_primary(self, symbol: str, timeframes: list, limit: int) -> dict:
        """Fetch from Binance (existing functionality enhanced)"""
        try:
            market_data = {}
            for timeframe in timeframes:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                market_data[timeframe] = df
            
            logger.info(f"✅ Binance: {symbol} data fetched successfully")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Binance fetch failed: {e}")
            return {}
    
    async def _fetch_backup(self, symbol: str, timeframes: list, limit: int) -> dict:
        """Fetch from Bybit as backup"""
        try:
            market_data = {}
            for timeframe in timeframes:
                ohlcv = self.backup_exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                market_data[timeframe] = df
            
            logger.info(f"✅ Bybit backup: {symbol} data fetched successfully")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Bybit backup failed: {e}")
            return {}
    
    async def _get_market_context(self, symbol: str) -> dict:
        """Get market sentiment from CoinGecko - NEW FEATURE"""
        try:
            coin_map = {
                'ETH/USDT': 'ethereum',
                'BTC/USDT': 'bitcoin', 
                'SOL/USDT': 'solana'
            }
            
            coin_id = coin_map.get(symbol, 'ethereum')
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                change_24h = coin_data.get('usd_24h_change', 0)
                
                return {
                    'price_change_24h': change_24h,
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'market_sentiment': 'bullish' if change_24h > 2 else ('bearish' if change_24h < -2 else 'neutral'),
                    'sentiment_strength': min(abs(change_24h) / 10, 1.0)  # 0-1 scale
                }
            
            return {'market_sentiment': 'neutral', 'sentiment_strength': 0.5}
            
        except Exception as e:
            logger.error(f"❌ CoinGecko context failed: {e}")
            return {'market_sentiment': 'neutral', 'sentiment_strength': 0.5}
    
    def get_current_price(self, symbol: str) -> dict:
        """Enhanced current price with backup - ENHANCED EXISTING"""
        try:
            # Try primary first
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['baseVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'source': 'binance'
            }
        except Exception as e:
            # Try backup
            if self.backup_exchange:
                try:
                    ticker = self.backup_exchange.fetch_ticker(symbol)
                    return {
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'],
                        'volume_24h': ticker['baseVolume'],
                        'high_24h': ticker['high'],
                        'low_24h': ticker['low'],
                        'source': 'bybit_backup'
                    }
                except:
                    pass
            
            logger.error(f"❌ Both price sources failed: {e}")
            return {}
    
    def get_anchor_candle(self, df: pd.DataFrame) -> dict:
        """Enhanced anchor candle with validation - ENHANCED EXISTING"""
        try:
            if len(df) < 2:
                logger.warning("⚠️ Insufficient data for anchor candle")
                return {}
                
            latest = df.iloc[-2]  # Use completed candle
            
            # Enhanced validation
            required_fields = ['open', 'high', 'low', 'close', 'volume']
            for field in required_fields:
                if pd.isna(latest[field]) or latest[field] <= 0:
                    logger.warning(f"⚠️ Invalid {field} in anchor candle")
                    return {}
            
            return {
                'timestamp': latest.name,
                'open': float(latest['open']),
                'high': float(latest['high']), 
                'low': float(latest['low']),
                'close': float(latest['close']),
                'volume': float(latest['volume']),
                'validated': True
            }
            
        except Exception as e:
            logger.error(f"❌ Anchor candle error: {e}")
            return {}
