"""
Professional report formatter for institutional-grade crypto analysis
"""
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ProfessionalReportFormatter:
    def __init__(self, config):
        self.config = config

    def generate_analysis_report(self, symbol: str, market_data: dict, analysis: dict, anchor_candle: dict, current_price_info: dict) -> str:
        """Generate complete professional analysis report"""
        try:
            # Header with timestamp
            timestamp = datetime.now().strftime('%d %b %Y – %H:%M %Z')
            symbol_clean = symbol.replace('/', '')

            # Get analysis data for both timeframes
            intraday_analysis = analysis.get('15m', {})
            swing_analysis = analysis.get('1d', {})

            # Calculate trade levels
            trade_levels = self._calculate_trade_levels(anchor_candle, intraday_analysis, swing_analysis)

            # Generate sentiment score
            sentiment = self._calculate_sentiment_score(intraday_analysis, swing_analysis)

            report = f"""
**{symbol_clean} | Professional Analysis | {timestamp}**

📊 **Anchor Candle** ({anchor_candle.get('timestamp', datetime.now()).strftime('%H:%M')})
**O:** {anchor_candle.get('open', 0):.2f} | **H:** {anchor_candle.get('high', 0):.2f} | **L:** {anchor_candle.get('low', 0):.2f} | **C:** {anchor_candle.get('close', 0):.2f}

📈 **TRADING MATRIX**
```
┌─────────────┬────────┬────────┬────────┬────────┬─────┬──────────┐
│ Timeframe   │ Action │ Entry  │ SL     │ TP     │ R:R │ Leverage │
├─────────────┼────────┼────────┼────────┼────────┼─────┼──────────┤
│ Intraday    │ {trade_levels['intraday']['action']:<6} │ {trade_levels['intraday']['entry']:<6.0f} │ {trade_levels['intraday']['sl']:<6.0f} │ {trade_levels['intraday']['tp']:<6.0f} │ {trade_levels['intraday']['rr']:<4} │ {self.config.INTRADAY_LEVERAGE}x       │
│ (15m–1h)    │        │        │        │        │     │          │
├─────────────┼────────┼────────┼────────┼────────┼─────┼──────────┤
│ Swing       │ {trade_levels['swing']['action']:<6} │ {trade_levels['swing']['entry']:<6.0f} │ {trade_levels['swing']['sl']:<6.0f} │ {trade_levels['swing']['tp']:<6.0f} │ {trade_levels['swing']['rr']:<4} │ {self.config.SWING_LEVERAGE}x       │
│ (4h–1d)     │        │        │        │        │     │          │
└─────────────┴────────┴────────┴────────┴────────┴─────┴──────────┘
```

🔑 **KEY LEVELS**
**🔑 Support:** {self._format_levels(intraday_analysis.get('support_resistance', {}).get('support', []))}
**⚔️ Resistance:** {self._format_levels(intraday_analysis.get('support_resistance', {}).get('resistance', []))}

⚡ **TECHNICAL SIGNALS**
**RSI (15m):** ~{intraday_analysis.get('rsi', {}).get('value', 0):.0f} ({intraday_analysis.get('rsi', {}).get('condition', 'neutral')})
**RSI (1D):** ~{swing_analysis.get('rsi', {}).get('value', 0):.0f} ({swing_analysis.get('rsi', {}).get('condition', 'neutral')})
**MACD (15m):** {intraday_analysis.get('macd', {}).get('condition', 'neutral').title()} crossover
**MACD (1D):** {swing_analysis.get('macd', {}).get('condition', 'neutral').title()} momentum
**OBV:** {intraday_analysis.get('obv', {}).get('trend', 'neutral').title()} pattern

📊 **SENTIMENT ANALYSIS**
**Short-term (15m–1h):** {sentiment['short_term']:.2f}
**Long-term (4h–1d):** {sentiment['long_term']:.2f}

🎯 **MARKET DRIVERS**
{self._generate_market_narrative(current_price_info, sentiment)}

🛡️ **RISK MANAGEMENT**
• Risk **1–2%** of capital per trade
• Move SL to **breakeven** once **+1%** in profit  
• Monitor **volume divergence** for early exits
• Adjust position size based on **volatility**

⚠️ **Disclaimer:** Educational analysis only. Not financial advice. Manage your own risk.

---
*Analysis generated at {datetime.now().strftime('%H:%M:%S %Z')} | Next update in 60 minutes*
"""

            return report.strip()

        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return f"❌ Error generating analysis for {symbol}: {str(e)}"

    def _calculate_trade_levels(self, anchor_candle: dict, intraday: dict, swing: dict) -> dict:
        """Calculate professional trade entry, SL, TP levels"""
        try:
            current_price = anchor_candle.get('close', 0)

            # Intraday levels (tighter stops)
            intraday_action = self._determine_action(intraday)
            if intraday_action == 'BUY':
                intraday_sl = current_price * 0.985  # 1.5% SL
                intraday_tp = current_price * 1.030  # 3% TP
            else:  # SELL
                intraday_sl = current_price * 1.015  # 1.5% SL  
                intraday_tp = current_price * 0.970  # 3% TP

            intraday_rr = abs((intraday_tp - current_price) / (intraday_sl - current_price))

            # Swing levels (wider stops)
            swing_action = self._determine_action(swing)
            if swing_action == 'BUY':
                swing_sl = current_price * 0.95   # 5% SL
                swing_tp = current_price * 1.10   # 10% TP  
            else:  # SELL
                swing_sl = current_price * 1.05   # 5% SL
                swing_tp = current_price * 0.90   # 10% TP

            swing_rr = abs((swing_tp - current_price) / (swing_sl - current_price))

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
            return {'intraday': {}, 'swing': {}}

    def _determine_action(self, analysis: dict) -> str:
        """Determine BUY/SELL action based on technical analysis"""
        try:
            trend = analysis.get('trend', 'neutral')
            rsi_condition = analysis.get('rsi', {}).get('condition', 'neutral')
            macd_condition = analysis.get('macd', {}).get('condition', 'neutral')

            bullish_signals = 0
            bearish_signals = 0

            # Count bullish signals
            if trend == 'bullish':
                bullish_signals += 1
            if rsi_condition in ['bullish', 'oversold']:
                bullish_signals += 1  
            if macd_condition == 'bullish':
                bullish_signals += 1

            # Count bearish signals
            if trend == 'bearish':
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
            return 'HOLD'

    def _format_levels(self, levels: List[float]) -> str:
        """Format support/resistance levels professionally"""
        if not levels:
            return "None identified"

        if len(levels) == 1:
            return f"{levels[0]:.0f}"
        else:
            return f"{min(levels):.0f}–{max(levels):.0f}"

    def _calculate_sentiment_score(self, intraday: dict, swing: dict) -> dict:
        """Calculate sentiment scores (0-1 scale)"""
        try:
            def analyze_sentiment(analysis):
                score = 0.5  # neutral base

                # Trend contribution (30%)
                if analysis.get('trend') == 'bullish':
                    score += 0.15
                elif analysis.get('trend') == 'bearish':
                    score -= 0.15

                # RSI contribution (25%)
                rsi_condition = analysis.get('rsi', {}).get('condition')
                if rsi_condition == 'bullish':
                    score += 0.125
                elif rsi_condition == 'oversold':
                    score += 0.125
                elif rsi_condition == 'bearish':
                    score -= 0.125
                elif rsi_condition == 'overbought':
                    score -= 0.125

                # MACD contribution (25%) 
                macd_condition = analysis.get('macd', {}).get('condition')
                if macd_condition == 'bullish':
                    score += 0.125
                elif macd_condition == 'bearish':
                    score -= 0.125

                # OBV contribution (20%)
                obv_trend = analysis.get('obv', {}).get('trend')
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
                narratives.append("• **Strong bullish momentum** → +{:.1f}% daily surge".format(change_24h))
            elif change_24h > 2:
                narratives.append("• **Moderate bullish bias** → +{:.1f}% daily gains".format(change_24h))
            elif change_24h < -5:
                narratives.append("• **Heavy selling pressure** → {:.1f}% daily decline".format(change_24h))
            elif change_24h < -2:
                narratives.append("• **Mild bearish pressure** → {:.1f}% daily dip".format(change_24h))
            else:
                narratives.append("• **Consolidation phase** → {:.1f}% daily range".format(change_24h))

            # Sentiment-based narrative
            avg_sentiment = (sentiment['short_term'] + sentiment['long_term']) / 2
            if avg_sentiment > 0.65:
                narratives.append("• **Market confidence high** → Multiple bullish confluences")
            elif avg_sentiment < 0.35:
                narratives.append("• **Caution warranted** → Multiple bearish signals present")
            else:
                narratives.append("• **Mixed signals** → Market in transition phase")

            # Volume narrative (placeholder - would need actual volume analysis)
            narratives.append("• **Institutional flows** → Monitor for breakout confirmation")

            return "\n".join(narratives)

        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return "• **Analysis in progress** → Gathering market data"
