"""
Professional report formatter for cryptocurrency analysis
"""
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger(__name__)

class ProfessionalReportFormatter:
    def __init__(self, config):
        self.config = config
        
    def generate_analysis_report(self, symbol: str, market_data: dict, analysis: dict, anchor_candle: dict, current_price_info: dict) -> str:
        """Generate complete professional analysis report"""
        try:
            timestamp = datetime.now().strftime('%d %b %Y – %H:%M %Z')
            symbol_clean = symbol.replace('/', '')
            
            # Get analysis data for both timeframes
            intraday_analysis = analysis.get('15m', {})
            swing_analysis = analysis.get('1d', {})
            
            # Calculate trade levels
            trade_levels = self._calculate_trade_levels(anchor_candle, intraday_analysis, swing_analysis)
            
            # Generate sentiment score
            sentiment = self._calculate_sentiment_score(intraday_analysis, swing_analysis)
            
            # Build report sections
            header = f"**{symbol_clean} | Professional Analysis | {timestamp}**\n\n"
            
            anchor_section = (
                f"📊 **Anchor Candle** ({anchor_candle.get('timestamp', datetime.now()).strftime('%H:%M')})\n"
                f"**O:** {anchor_candle.get('open', 0):.2f} | **H:** {anchor_candle.get('high', 0):.2f} | "
                f"**L:** {anchor_candle.get('low', 0):.2f} | **C:** {anchor_candle.get('close', 0):.2f}\n\n"
            )
            
            # Trading matrix (using text formatting instead of ASCII table to avoid backtick issues)
            matrix_section = (
                f"📈 **TRADING MATRIX**\n"
                f"**Intraday (15m-1h):** {trade_levels['intraday']['action']} | "
                f"Entry: {trade_levels['intraday']['entry']:.0f} | "
                f"SL: {trade_levels['intraday']['sl']:.0f} | "
                f"TP: {trade_levels['intraday']['tp']:.0f} | "
                f"R:R: {trade_levels['intraday']['rr']} | "
                f"Leverage: {self.config.INTRADAY_LEVERAGE}x\n"
                f"**Swing (4h-1d):** {trade_levels['swing']['action']} | "
                f"Entry: {trade_levels['swing']['entry']:.0f} | "
                f"SL: {trade_levels['swing']['sl']:.0f} | "
                f"TP: {trade_levels['swing']['tp']:.0f} | "
                f"R:R: {trade_levels['swing']['rr']} | "
                f"Leverage: {self.config.SWING_LEVERAGE}x\n\n"
            )
            
            levels_section = (
                f"🔑 **KEY LEVELS**\n"
                f"**🔑 Support:** {self._format_levels(intraday_analysis.get('support_resistance', {}).get('support', []))}\n"
                f"**⚔️ Resistance:** {self._format_levels(intraday_analysis.get('support_resistance', {}).get('resistance', []))}\n\n"
            )
            
            signals_section = (
                f"⚡ **TECHNICAL SIGNALS**\n"
                f"**RSI (15m):** ~{intraday_analysis.get('rsi', {}).get('value', 0):.0f} ({intraday_analysis.get('rsi', {}).get('condition', 'neutral')})\n"
                f"**RSI (1D):** ~{swing_analysis.get('rsi', {}).get('value', 0):.0f} ({swing_analysis.get('rsi', {}).get('condition', 'neutral')})\n"
                f"**MACD (15m):** {intraday_analysis.get('macd', {}).get('condition', 'neutral').title()} crossover\n"
                f"**MACD (1D):** {swing_analysis.get('macd', {}).get('condition', 'neutral').title()} momentum\n"
                f"**OBV:** {intraday_analysis.get('obv', {}).get('trend', 'neutral').title()} pattern\n\n"
            )
            
            sentiment_section = (
                f"📊 **SENTIMENT ANALYSIS**\n"
                f"**Short-term (15m–1h):** {sentiment['short_term']:.2f}\n"
                f"**Long-term (4h–1d):** {sentiment['long_term']:.2f}\n\n"
            )
            
            narrative_section = (
                f"🎯 **MARKET DRIVERS**\n"
                f"{self._generate_market_narrative(current_price_info, sentiment)}\n\n"
            )
            
            risk_section = (
                f"🛡️ **RISK MANAGEMENT**\n"
                f"• Risk **1–2%** of capital per trade\n"
                f"• Move SL to **breakeven** once **+1%** in profit\n"
                f"• Monitor **volume divergence** for early exits\n"
                f"• Adjust position size based on **volatility**\n\n"
            )
            
            footer = (
                f"⚠️ **Disclaimer:** Educational analysis only. Not financial advice. Manage your own risk.\n\n"
                f"---\n"
                f"*Analysis generated at {datetime.now().strftime('%H:%M:%S %Z')} | Next update in 60 minutes*"
            )
            
            # Combine all sections
            report = header + anchor_section + matrix_section + levels_section + signals_section + sentiment_section + narrative_section + risk_section + footer
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return f"❌ Error generating analysis for {symbol}: {str(e)}"
    
    def _calculate_trade_levels(self, anchor_candle: dict, intraday: dict, swing: dict) -> dict:
        """Calculate professional trade entry, SL, TP levels"""
        try:
            current_price = anchor_candle.get('close', 0)
            if current_price == 0:
                current_price = 1000  # Default fallback
            
            # Intraday levels (tighter stops)
            intraday_action = self._determine_action(intraday)
            if intraday_action == 'BUY':
                intraday_sl = current_price * 0.985  # 1.5% SL
                intraday_tp = current_price * 1.030  # 3% TP
            else:  # SELL or HOLD
                intraday_sl = current_price * 1.015  # 1.5% SL  
                intraday_tp = current_price * 0.970  # 3% TP
            
            intraday_rr = abs((intraday_tp - current_price) / (intraday_sl - current_price)) if intraday_sl != current_price else 1.0
            
            # Swing levels (wider stops)
            swing_action = self._determine_action(swing)
            if swing_action == 'BUY':
                swing_sl = current_price * 0.95   # 5% SL
                swing_tp = current_price * 1.10   # 10% TP  
            else:  # SELL or HOLD
                swing_sl = current_price * 1.05   # 5% SL
                swing_tp = current_price * 0.90   # 10% TP
                
            swing_rr = abs((swing_tp - current_price) / (swing_sl - current_price)) if swing_sl != current_price else 1.0
            
            return {
                'intraday': {
                    'action': intraday_action,
                    'entry': current_price,
                    'sl': intraday_sl,
                    'tp': intraday_tp,
                    'rr': f"{intraday_rr:.1f}"
                },
                'swing': {
                    'action': swing_action, 
                    'entry': current_price,
                    'sl': swing_sl,
                    'tp': swing_tp,
                    'rr': f"{swing_rr:.1f}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating trade levels: {e}")
            return {
                'intraday': {'action': 'HOLD', 'entry': 0, 'sl': 0, 'tp': 0, 'rr': '1.0'},
                'swing': {'action': 'HOLD', 'entry': 0, 'sl': 0, 'tp': 0, 'rr': '1.0'}
            }
    
    def _determine_action(self, analysis: dict) -> str:
        """Determine BUY/SELL action based on technical analysis"""
        try:
            if not analysis:
                return 'HOLD'
                
            trend = analysis.get('trend', 'neutral')
            rsi_condition = analysis.get('rsi', {}).get('condition', 'neutral')
            macd_condition = analysis.get('macd', {}).get('condition', 'neutral')
            
            bullish_signals = 0
            bearish_signals = 0
            
            # Count bullish signals
            if trend in ['bullish', 'strong_bullish']:
                bullish_signals += 1
            if rsi_condition in ['bullish', 'oversold']:
                bullish_signals += 1  
            if macd_condition == 'bullish':
                bullish_signals += 1
                
            # Count bearish signals
            if trend in ['bearish', 'strong_bearish']:
                bearish_signals += 1
            if rsi_condition in ['bearish', 'overbought']:
                bearish_signals += 1
            if macd_condition == 'bearish': 
                bearish_signals += 1
            
            if bullish_signals > bearish_signals:
                return 'BUY'
            elif bearish_signals > bullish_signals:
                return 'SELL'
            else:
                return 'HOLD'
                
        except Exception as e:
            logger.error(f"Action determination error: {e}")
            return 'HOLD'
    
    def _format_levels(self, levels: List[float]) -> str:
        """Format support/resistance levels professionally"""
        try:
            if not levels or len(levels) == 0:
                return "None identified"
            
            valid_levels = [level for level in levels if level > 0]
            if not valid_levels:
                return "Analysis pending"
            
            if len(valid_levels) == 1:
                return f"{valid_levels[0]:.0f}"
            else:
                return f"{min(valid_levels):.0f}–{max(valid_levels):.0f}"
        except Exception as e:
            logger.error(f"Level formatting error: {e}")
            return "Error formatting levels"
    
    def _calculate_sentiment_score(self, intraday: dict, swing: dict) -> dict:
        """Calculate sentiment scores (0-1 scale)"""
        try:
            def analyze_sentiment(analysis):
                if not analysis:
                    return 0.5
                    
                score = 0.5  # neutral base
                
                # Trend contribution (30%)
                trend = analysis.get('trend', 'neutral')
                if trend in ['bullish', 'strong_bullish']:
                    score += 0.15
                elif trend in ['bearish', 'strong_bearish']:
                    score -= 0.15
                    
                # RSI contribution (25%)
                rsi_condition = analysis.get('rsi', {}).get('condition', 'neutral')
                if rsi_condition in ['bullish', 'oversold']:
                    score += 0.125
                elif rsi_condition in ['bearish', 'overbought']:
                    score -= 0.125
                    
                # MACD contribution (25%) 
                macd_condition = analysis.get('macd', {}).get('condition', 'neutral')
                if macd_condition == 'bullish':
                    score += 0.125
                elif macd_condition == 'bearish':
                    score -= 0.125
                    
                # OBV contribution (20%)
                obv_trend = analysis.get('obv', {}).get('trend', 'neutral')
                if obv_trend == 'accumulation':
                    score += 0.1
                elif obv_trend == 'distribution':
                    score -= 0.1
                
                return max(0.0, min(1.0, score))  # Clamp between 0-1
            
            return {
                'short_term': analyze_sentiment(intraday),
                'long_term': analyze_sentiment(swing)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment: {e}")
            return {'short_term': 0.5, 'long_term': 0.5}
    
    def _generate_market_narrative(self, price_info: dict, sentiment: dict) -> str:
        """Generate market narrative based on current conditions"""
        try:
            change_24h = price_info.get('change_24h', 0)
            
            narratives = []
            
            # Price action narrative
            if change_24h > 5:
                narratives.append(f"• **Strong bullish momentum** → +{change_24h:.1f}% daily surge")
            elif change_24h > 2:
                narratives.append(f"• **Moderate bullish bias** → +{change_24h:.1f}% daily gains")
            elif change_24h < -5:
                narratives.append(f"• **Heavy selling pressure** → {change_24h:.1f}% daily decline")
            elif change_24h < -2:
                narratives.append(f"• **Mild bearish pressure** → {change_24h:.1f}% daily dip")
            else:
                narratives.append(f"• **Consolidation phase** → {change_24h:.1f}% daily range")
            
            # Sentiment-based narrative
            short_term = sentiment.get('short_term', 0.5)
            long_term = sentiment.get('long_term', 0.5)
            avg_sentiment = (short_term + long_term) / 2
            
            if avg_sentiment > 0.65:
                narratives.append("• **Market confidence high** → Multiple bullish confluences")
            elif avg_sentiment < 0.35:
                narratives.append("• **Caution warranted** → Multiple bearish signals present")
            else:
                narratives.append("• **Mixed signals** → Market in transition phase")
            
            # Additional context
            narratives.append("• **Institutional flows** → Monitor for breakout confirmation")
            
            return "\n".join(narratives)
            
        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return "• **Analysis in progress** → Gathering market data"

