"""
Enhanced technical analysis with TA-Lib fallbacks and advanced indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ProfessionalAnalysis:
    def __init__(self):
        # Try to import TA-Lib, fallback to manual calculations
        self.use_talib = False
        try:
            import talib
            self.talib = talib
            self.use_talib = True
            logger.info("✅ TA-Lib available - using optimized calculations")
        except ImportError:
            logger.info("⚠️ TA-Lib not available - using manual calculations")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Enhanced RSI with TA-Lib fallback"""
        try:
            if self.use_talib:
                rsi_values = self.talib.RSI(prices.values, timeperiod=period)
                return pd.Series(rsi_values, index=prices.index)
            else:
                # Manual calculation fallback
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return 100 - (100 / (1 + rs))
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return pd.Series(index=prices.index)
    
    def calculate_macd(self, prices: pd.Series, fast=12, slow=26, signal=9) -> Dict:
        """Enhanced MACD with TA-Lib fallback"""
        try:
            if self.use_talib:
                macd, signal_line, histogram = self.talib.MACD(prices.values, 
                                                             fastperiod=fast, 
                                                             slowperiod=slow, 
                                                             signalperiod=signal)
                return {
                    'macd': pd.Series(macd, index=prices.index),
                    'signal': pd.Series(signal_line, index=prices.index),
                    'histogram': pd.Series(histogram, index=prices.index)
                }
            else:
                # Manual calculation fallback
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
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict:
        """NEW: Bollinger Bands calculation"""
        try:
            if self.use_talib:
                upper, middle, lower = self.talib.BBANDS(prices.values, 
                                                       timeperiod=period, 
                                                       nbdevup=std_dev, 
                                                       nbdevdn=std_dev)
                return {
                    'upper': pd.Series(upper, index=prices.index),
                    'middle': pd.Series(middle, index=prices.index),
                    'lower': pd.Series(lower, index=prices.index)
                }
            else:
                sma = prices.rolling(period).mean()
                std = prices.rolling(period).std()
                return {
                    'upper': sma + (std * std_dev),
                    'middle': sma,
                    'lower': sma - (std * std_dev)
                }
        except Exception as e:
            logger.error(f"Bollinger Bands error: {e}")
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series()}
    
    def identify_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """ENHANCED: Better support/resistance identification"""
        try:
            # Find pivot points using rolling max/min
            highs = df['high'].rolling(window=window, center=True).max()
            lows = df['low'].rolling(window=window, center=True).min()
            
            # Identify pivot highs and lows
            pivot_highs = df[df['high'] == highs]['high'].dropna().tail(5)
            pivot_lows = df[df['low'] == lows]['low'].dropna().tail(5)
            
            current_price = df['close'].iloc[-1]
            
            # Filter relevant levels
            resistance_levels = pivot_highs[pivot_highs > current_price * 1.001].tolist()
            support_levels = pivot_lows[pivot_lows < current_price * 0.999].tolist()
            
            return {
                'resistance': resistance_levels[-3:] if resistance_levels else [current_price * 1.02],
                'support': support_levels[-3:] if support_levels else [current_price * 0.98],
                'current_price': current_price,
                'strength': len(resistance_levels) + len(support_levels)  # Level strength indicator
            }
            
        except Exception as e:
            logger.error(f"S/R calculation error: {e}")
            return {'resistance': [], 'support': [], 'current_price': 0, 'strength': 0}
    
    def calculate_volume_profile(self, df: pd.DataFrame) -> Dict:
        """NEW: Volume profile analysis"""
        try:
            # Simple volume profile approximation
            price_bins = pd.cut(df['close'], bins=20)
            volume_by_price = df.groupby(price_bins)['volume'].sum()
            
            # Find Point of Control (POC) - highest volume area
            poc_bin = volume_by_price.idxmax()
            poc_price = (poc_bin.left + poc_bin.right) / 2
            
            # Value Area (70% of volume)
            total_volume = volume_by_price.sum()
            value_area_volume = total_volume * 0.7
            
            return {
                'poc': float(poc_price) if not pd.isna(poc_price) else df['close'].iloc[-1],
                'total_volume': float(total_volume),
                'distribution': 'balanced' if abs(poc_price - df['close'].iloc[-1]) / df['close'].iloc[-1] < 0.02 else 'skewed'
            }
            
        except Exception as e:
            logger.error(f"Volume profile error: {e}")
            return {'poc': df['close'].iloc[-1] if not df.empty else 0, 'distribution': 'unknown'}
    
    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """ENHANCED: Enhanced timeframe analysis with new indicators"""
        try:
            if df.empty:
                return {'error': 'Empty dataframe'}
            
            analysis = {}
            current_price = df['close'].iloc[-1]
            analysis['current_price'] = current_price
            
            # Enhanced RSI Analysis
            rsi = self.calculate_rsi(df['close'])
            if not rsi.empty:
                current_rsi = rsi.iloc[-1]
                rsi_trend = 'rising' if rsi.iloc[-1] > rsi.iloc[-3] else 'falling'
                analysis['rsi'] = {
                    'value': current_rsi,
                    'condition': self._enhanced_rsi_condition(current_rsi),
                    'trend': rsi_trend
                }
            
            # Enhanced MACD Analysis  
            macd_data = self.calculate_macd(df['close'])
            if not macd_data['macd'].empty:
                macd_condition = self._enhanced_macd_condition(macd_data)
                crossover = self._detect_macd_crossover(macd_data)
                
                analysis['macd'] = {
                    'macd': macd_data['macd'].iloc[-1],
                    'signal': macd_data['signal'].iloc[-1],
                    'histogram': macd_data['histogram'].iloc[-1],
                    'condition': macd_condition,
                    'crossover': crossover
                }
            
            # NEW: Bollinger Bands
            bb_data = self.calculate_bollinger_bands(df['close'])
            if not bb_data['middle'].empty:
                bb_position = self._determine_bb_position(current_price, bb_data)
                analysis['bollinger'] = {
                    'position': bb_position,
                    'squeeze': self._detect_bb_squeeze(bb_data)
                }
            
            # Enhanced Support/Resistance
            sr_levels = self.identify_support_resistance(df)
            analysis['support_resistance'] = sr_levels
            
            # NEW: Volume Profile
            volume_analysis = self.calculate_volume_profile(df)
            analysis['volume_profile'] = volume_analysis
            
            # Enhanced OBV
            obv = self.calculate_obv(df)
            if not obv.empty:
                obv_trend = 'accumulation' if obv.iloc[-1] > obv.iloc[-5] else 'distribution'
                analysis['obv'] = {
                    'value': obv.iloc[-1],
                    'trend': obv_trend
                }
            
            # Enhanced trend determination
            analysis['trend'] = self._determine_enhanced_trend(df, analysis)
            analysis['timeframe'] = timeframe
            analysis['confidence'] = self._calculate_confidence_score(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Enhanced analysis error for {timeframe}: {e}")
            return {'error': str(e), 'timeframe': timeframe}
    
    def _enhanced_rsi_condition(self, rsi: float) -> str:
        """Enhanced RSI interpretation"""
        if rsi > 80:
            return 'extremely_overbought'
        elif rsi > 70:
            return 'overbought'
        elif rsi > 60:
            return 'bullish'
        elif rsi > 40:
            return 'neutral'
        elif rsi > 30:
            return 'bearish'
        elif rsi > 20:
            return 'oversold'
        else:
            return 'extremely_oversold'
    
    def _enhanced_macd_condition(self, macd_data: dict) -> str:
        """Enhanced MACD analysis"""
        try:
            macd = macd_data['macd'].iloc[-1]
            signal = macd_data['signal'].iloc[-1]
            histogram = macd_data['histogram'].iloc[-1]
            
            if macd > signal and histogram > 0:
                return 'bullish'
            elif macd < signal and histogram < 0:
                return 'bearish'
            else:
                return 'neutral'
        except:
            return 'neutral'
    
    def _detect_macd_crossover(self, macd_data: dict) -> str:
        """Detect MACD crossovers"""
        try:
            current_histogram = macd_data['histogram'].iloc[-1]
            previous_histogram = macd_data['histogram'].iloc[-2]
            
            if current_histogram > 0 and previous_histogram <= 0:
                return 'bullish_crossover'
            elif current_histogram < 0 and previous_histogram >= 0:
                return 'bearish_crossover'
            else:
                return 'no_crossover'
        except:
            return 'no_crossover'
    
    def _determine_bb_position(self, price: float, bb_data: dict) -> str:
        """Determine Bollinger Band position"""
        try:
            upper = bb_data['upper'].iloc[-1]
            middle = bb_data['middle'].iloc[-1]
            lower = bb_data['lower'].iloc[-1]
            
            if price > upper:
                return 'above_upper'
            elif price > middle:
                return 'upper_half'
            elif price > lower:
                return 'lower_half'
            else:
                return 'below_lower'
        except:
            return 'unknown'
    
    def _detect_bb_squeeze(self, bb_data: dict) -> bool:
        """Detect Bollinger Band squeeze"""
        try:
            current_width = bb_data['upper'].iloc[-1] - bb_data['lower'].iloc[-1]
            avg_width = (bb_data['upper'] - bb_data['lower']).rolling(20).mean().iloc[-1]
            return current_width < avg_width * 0.8
        except:
            return False
    
    def _determine_enhanced_trend(self, df: pd.DataFrame, analysis: dict) -> str:
        """Enhanced trend determination with multiple factors"""
        try:
            current_price = df['close'].iloc[-1]
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1]
            
            # Price vs SMAs
            price_trend_score = 0
            if current_price > sma_20 > sma_50:
                price_trend_score = 2
            elif current_price > sma_20:
                price_trend_score = 1
            elif current_price < sma_20 < sma_50:
                price_trend_score = -2
            elif current_price < sma_20:
                price_trend_score = -1
            
            # RSI contribution
            rsi_condition = analysis.get('rsi', {}).get('condition', 'neutral')
            rsi_score = 0
            if rsi_condition in ['bullish', 'oversold']:
                rsi_score = 1
            elif rsi_condition in ['bearish', 'overbought']:
                rsi_score = -1
            
            # MACD contribution
            macd_condition = analysis.get('macd', {}).get('condition', 'neutral')
            macd_score = 0
            if macd_condition == 'bullish':
                macd_score = 1
            elif macd_condition == 'bearish':
                macd_score = -1
            
            # Total score
            total_score = price_trend_score + rsi_score + macd_score
            
            if total_score >= 3:
                return 'strong_bullish'
            elif total_score >= 1:
                return 'bullish'
            elif total_score <= -3:
                return 'strong_bearish'
            elif total_score <= -1:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Trend determination error: {e}")
            return 'neutral'
    
    def _calculate_confidence_score(self, analysis: dict) -> float:
        """Calculate overall analysis confidence (0-100)"""
        try:
            confidence = 50.0  # Base confidence
            
            # RSI confidence
            rsi_condition = analysis.get('rsi', {}).get('condition', 'neutral')
            if rsi_condition in ['bullish', 'bearish', 'oversold', 'overbought']:
                confidence += 15
            
            # MACD confidence
            macd_condition = analysis.get('macd', {}).get('condition', 'neutral')
            if macd_condition in ['bullish', 'bearish']:
                confidence += 15
            
            # Crossover confidence
            crossover = analysis.get('macd', {}).get('crossover', 'no_crossover')
            if 'crossover' in crossover:
                confidence += 10
            
            # Support/Resistance strength
            sr_strength = analysis.get('support_resistance', {}).get('strength', 0)
            confidence += min(sr_strength * 2, 10)
            
            return min(max(confidence, 0), 100)
            
        except:
            return 50.0
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume (existing method kept)"""
        try:
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
        except:
            return pd.Series(index=df.index)


