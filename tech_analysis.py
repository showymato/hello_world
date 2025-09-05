"""
Professional technical analysis engine for institutional-grade reports
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ProfessionalAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI with professional precision"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(prices: pd.Series, fast=12, slow=26, signal=9) -> Dict:
        """Calculate MACD with signal and histogram"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line, 
            'histogram': histogram
        }

    @staticmethod
    def identify_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict:
        """Identify key support and resistance zones"""
        try:
            # Calculate pivot points
            highs = df['high'].rolling(window=window, center=True).max()
            lows = df['low'].rolling(window=window, center=True).min()

            # Find pivot highs and lows
            pivot_highs = df[df['high'] == highs]['high'].dropna()
            pivot_lows = df[df['low'] == lows]['low'].dropna()

            # Get recent levels
            current_price = df['close'].iloc[-1]

            # Resistance levels (above current price)
            resistance_levels = pivot_highs[pivot_highs > current_price].tail(3)
            support_levels = pivot_lows[pivot_lows < current_price].tail(3)

            return {
                'resistance': list(resistance_levels) if len(resistance_levels) > 0 else [current_price * 1.05],
                'support': list(support_levels) if len(support_levels) > 0 else [current_price * 0.95],
                'current_price': current_price
            }

        except Exception as e:
            logger.error(f"Error identifying S/R levels: {e}")
            return {'resistance': [], 'support': [], 'current_price': 0}

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = pd.Series(index=df.index, dtype='float64')
        obv.iloc[0] = df['volume'].iloc[0]

        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Complete technical analysis for a timeframe"""
        try:
            analysis = {}

            # Price action
            current_price = df['close'].iloc[-1]
            analysis['current_price'] = current_price

            # RSI Analysis
            rsi = self.calculate_rsi(df['close'])
            current_rsi = rsi.iloc[-1]
            analysis['rsi'] = {
                'value': current_rsi,
                'condition': self._rsi_condition(current_rsi)
            }

            # MACD Analysis  
            macd_data = self.calculate_macd(df['close'])
            current_macd = macd_data['macd'].iloc[-1]
            current_signal = macd_data['signal'].iloc[-1]
            current_hist = macd_data['histogram'].iloc[-1]

            analysis['macd'] = {
                'macd': current_macd,
                'signal': current_signal,
                'histogram': current_hist,
                'condition': self._macd_condition(current_macd, current_signal, current_hist)
            }

            # Support/Resistance
            sr_levels = self.identify_support_resistance(df)
            analysis['support_resistance'] = sr_levels

            # OBV Analysis
            obv = self.calculate_obv(df)
            obv_trend = 'accumulation' if obv.iloc[-1] > obv.iloc[-5] else 'distribution'
            analysis['obv'] = {
                'value': obv.iloc[-1],
                'trend': obv_trend
            }

            # Overall trend
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1]

            if current_price > sma_20 > sma_50:
                trend = 'bullish'
            elif current_price < sma_20 < sma_50:
                trend = 'bearish' 
            else:
                trend = 'neutral'

            analysis['trend'] = trend
            analysis['timeframe'] = timeframe

            return analysis

        except Exception as e:
            logger.error(f"Error in technical analysis for {timeframe}: {e}")
            return {}

    def _rsi_condition(self, rsi: float) -> str:
        """Determine RSI condition"""
        if rsi > 70:
            return 'overbought'
        elif rsi < 30:
            return 'oversold'
        elif rsi > 50:
            return 'bullish'
        else:
            return 'bearish'

    def _macd_condition(self, macd: float, signal: float, histogram: float) -> str:
        """Determine MACD condition"""
        if macd > signal and histogram > 0:
            return 'bullish'
        elif macd < signal and histogram < 0:
            return 'bearish'
        else:
            return 'neutral'
