"""
Enhanced professional report formatter with market context integration
"""
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ProfessionalReportFormatter:
    def __init__(self, config):
        self.config = config
        
    def generate_analysis_report(self, symbol: str, market_data: dict, analysis: dict, anchor_candle: dict, current_price_info: dict) -> str:
        """ENHANCED: Generate analysis report with market context"""
        try:
            timestamp = datetime.now().strftime('%d %b %Y – %H:%M %Z')
            symbol_clean = symbol.replace('/', '')
            
            # Get analysis data
            intraday_analysis = analysis.get('15m', {})
            swing_analysis = analysis.get('1d', {})
            market_context = market_data.get('market_context', {})
            
            # Enhanced trade levels with confidence scores
            trade_levels = self._calculate_enhanced_trade_levels(anchor_candle, intraday_analysis, swing_analysis)
            
            # Enhanced sentiment with market context
            sentiment = self._calculate_enhanced_sentiment(intraday_analysis, swing_analysis, market_context)
            
            # Market context summary
            context_summary = self._generate_market_context_summary(market_context, current_price_info)
            
            report = f"""
**{symbol_clean} | Enhanced Professional Analysis | {timestamp}**

📊 **Anchor Candle** ({anchor_candle.get('timestamp', datetime.now()).strftime('%H:%M')})
**O:** {anchor_candle.get('open', 0):.2f} | **H:** {anchor_candle.get('high', 0):.2f} | **L:** {anchor_candle.get('low', 0):.2f} | **C:** {anchor_candle.get('close', 0):.2f}

📈 **ENHANCED TRADING MATRIX**
