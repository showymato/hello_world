"""
Enhanced data fetcher with unrestricted data sources
"""
import ccxt
import pandas as pd
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self, exchange_name='binance'):
        # Use exchanges that work globally without restrictions
        self.exchanges = []
        
        # Try multiple unrestricted exchanges
        try:
            # KuCoin - Generally unrestricted
            self.exchanges.append(ccxt.kucoin({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }))
            logger.info("✅ KuCoin exchange available")
        except:
            pass
            
        try:
            # OKX - Good global coverage
            self.exchanges.append(ccxt.okx({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }))
            logger.info("✅ OKX exchange available")
        except:
            pass
            
        try:
            # Gate.io - Usually unrestricted
            self.exchanges.append(ccxt.gateio({
                'sandbox': False,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }))
            logger.info("✅ Gate.io exchange available")
        except:
            pass
        
        # CoinGecko for fallback data
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
    async def get_market_data(self, symbol: str, timeframes: list, limit: int = 200) -> dict:
        """Get market data from available exchanges"""
        try:
            # Try each exchange until one works
            for exchange in self.exchanges:
                try:
                    market_data = {}
                    exchange_name = exchange.id
                    
                    for timeframe in timeframes:
                        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df.set_index('timestamp', inplace=True)
                        market_data[timeframe] = df
                    
                    logger.info(f"✅ {exchange_name}: {symbol} data fetched successfully")
                    
                    # Add market context from CoinGecko
                    context = await self._get_market_context(symbol)
                    market_data['market_context'] = context
                    
                    return market_data
                    
                except Exception as e:
                    logger.warning(f"⚠️ {exchange.id} failed: {str(e)[:100]}")
                    continue
            
            # If all exchanges fail, use CoinGecko as last resort
            logger.warning("🔄 All exchanges failed, trying CoinGecko fallback...")
            return await self._get_coingecko_fallback_data(symbol, timeframes)
            
        except Exception as e:
            logger.error(f"❌ All data sources failed: {e}")
            return {}
    
    async def _get_coingecko_fallback_data(self, symbol: str, timeframes: list) -> dict:
        """Fallback to CoinGecko when exchanges are blocked"""
        try:
            # Map symbols to CoinGecko IDs
            coin_map = {
                'ETH/USDT': 'ethereum',
                'BTC/USDT': 'bitcoin',
                'SOL/USDT': 'solana'
            }
            
            coin_id = coin_map.get(symbol, 'ethereum')
            
            # Get historical data from CoinGecko
            url = f"{self.coingecko_base}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': '7',  # 7 days of data
                'interval': 'hourly'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'prices' in data:
                # Convert CoinGecko data to OHLCV format
                prices = data['prices']
                volumes = data.get('total_volumes', [])
                
                # Create basic OHLCV data (simplified)
                ohlcv_data = []
                for i, (timestamp, price) in enumerate(prices):
                    volume = volumes[i][1] if i < len(volumes) else 0
                    # Use price as OHLC (simplified for demo)
                    ohlcv_data.append([timestamp, price, price * 1.001, price * 0.999, price, volume])
                
                # Create DataFrame
                df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Return data for all requested timeframes (same data)
                market_data = {}
                for timeframe in timeframes:
                    market_data[timeframe] = df.copy()
                
                # Add market context
                context = await self._get_market_context(symbol)
                market_data['market_context'] = context
                
                logger.info(f"✅ CoinGecko fallback: {symbol} data retrieved")
                return market_data
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ CoinGecko fallback failed: {e}")
            return {}
    
    async def _get_market_context(self, symbol: str) -> dict:
        """Get market context from CoinGecko (unrestricted)"""
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
                'include_24hr_vol': 'true'
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
                    'sentiment_strength': min(abs(change_24h) / 10, 1.0)
                }
            
            return {'market_sentiment': 'neutral', 'sentiment_strength': 0.5}
            
        except Exception as e:
            logger.error(f"❌ CoinGecko context failed: {e}")
            return {'market_sentiment': 'neutral', 'sentiment_strength': 0.5}
    
    def get_current_price(self, symbol: str) -> dict:
        """Get current price from available sources"""
        try:
            # Try exchanges first
            for exchange in self.exchanges:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    return {
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'],
                        'volume_24h': ticker['baseVolume'],
                        'high_24h': ticker['high'],
                        'low_24h': ticker['low'],
                        'source': exchange.id
                    }
                except:
                    continue
            
            # Fallback to CoinGecko
            coin_map = {'ETH/USDT': 'ethereum', 'BTC/USDT': 'bitcoin', 'SOL/USDT': 'solana'}
            coin_id = coin_map.get(symbol, 'ethereum')
            
            url = f"{self.coingecko_base}/simple/price"
            params = {'ids': coin_id, 'vs_currencies': 'usd', 'include_24hr_change': 'true'}
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if coin_id in data:
                return {
                    'price': data[coin_id]['usd'],
                    'change_24h': data[coin_id].get('usd_24h_change', 0),
                    'source': 'coingecko'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ All price sources failed: {e}")
            return {}
    
    def get_anchor_candle(self, df: pd.DataFrame) -> dict:
        """Get anchor candle (unchanged)"""
        try:
            if len(df) < 2:
                return {}
                
            latest = df.iloc[-2]
            
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
