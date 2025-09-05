"""
Professional Crypto Analysis Bot - Main Application
Generates institutional-grade analysis reports for ETHUSDT and other crypto pairs
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd  # Added import

# Import modules with error handling
try:
    from config import AnalysisConfig
    from data_fetcher import CryptoDataFetcher
    from tech_analysis import ProfessionalAnalysis
    from report_formatter import ProfessionalReportFormatter
    from telegram_controller import AnalysisTelegramController
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all modules are present in the same directory")
    sys.exit(1)

# Setup professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProfessionalCryptoAnalysisBot:
    def __init__(self):
        """Initialize the professional analysis bot"""
        try:
            logger.info("🚀 Initializing Professional Crypto Analysis Bot...")
            self.config = AnalysisConfig()
            self.data_fetcher = CryptoDataFetcher(self.config.EXCHANGE)
            self.technical_analysis = ProfessionalAnalysis()
            self.report_formatter = ProfessionalReportFormatter(self.config)
            self.telegram = AnalysisTelegramController(self.config)
            self.is_running = False
            self.last_analysis_time = None
            logger.info("✅ Professional Analysis Bot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise

    async def generate_complete_analysis(self, symbol: str = None) -> str:
        """Generate complete professional analysis report"""
        try:
            if not symbol:
                symbol = self.config.DEFAULT_SYMBOL
            logger.info(f"📊 Generating professional analysis for {symbol}...")
            # Fetch market data for multiple timeframes
            timeframes = ['15m', '1h', '4h', '1d']
            market_data = await self.data_fetcher.get_market_data(symbol, timeframes)
            if not market_data:
                return f"❌ Unable to fetch market data for {symbol}"
            # Get current price information
            current_price_info = self.data_fetcher.get_current_price(symbol)
            # Get anchor candle (latest completed candle)
            anchor_candle = {}
            if '15m' in market_data and isinstance(market_data['15m'], pd.DataFrame):
                anchor_candle = self.data_fetcher.get_anchor_candle(market_data['15m'])
            # Perform technical analysis for each timeframe
            analysis_results = {}
            for timeframe, df in market_data.items():
                # Skip market_context dict
                if timeframe == 'market_context':
                    continue
                # Ensure type is DataFrame and not empty
                if isinstance(df, pd.DataFrame) and not df.empty:
                    try:
                        analysis_results[timeframe] = self.technical_analysis.analyze_timeframe(df, timeframe)
                        logger.info(f"✅ Analysis completed for {timeframe}")
                    except Exception as e:
                        logger.error(f"❌ Analysis failed for {timeframe}: {e}")
                        continue
                else:
                    logger.warning(f"⚠️ Skipping {timeframe}: not a valid DataFrame")
            # Generate professional report
            professional_report = self.report_formatter.generate_analysis_report(
                symbol=symbol,
                market_data=market_data,
                analysis=analysis_results,
                anchor_candle=anchor_candle,
                current_price_info=current_price_info
            )
            self.last_analysis_time = datetime.now()
            logger.info(f"✅ Professional analysis generated for {symbol}")
            return professional_report
        except Exception as e:
            logger.error(f"❌ Error generating analysis: {e}")
            return f"❌ Analysis generation failed for {symbol}: {str(e)}"

    async def run_automated_analysis(self):
        """Run automated analysis loop"""
        try:
            logger.info("🔄 Starting automated analysis monitoring...")
            self.is_running = True
            while self.is_running:
                try:
                    # Generate analysis for primary symbol
                    report = await self.generate_complete_analysis()
                    # Send via Telegram if configured
                    if self.telegram.initialized:
                        await self.telegram.send_analysis_report(report)
                    else:
                        logger.info("📊 Analysis generated (Telegram not configured)")
                        logger.info(f"Preview: {report[:200]}...")
                    # Wait for next analysis cycle (60 minutes)
                    await asyncio.sleep(self.config.ANALYSIS_INTERVAL * 60)
                except Exception as e:
                    logger.error(f"❌ Error in analysis loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        except Exception as e:
            logger.error(f"❌ Fatal error in automated analysis: {e}")

    async def manual_analysis(self, symbol: str = None) -> str:
        """Generate manual analysis on demand"""
        return await self.generate_complete_analysis(symbol)

    def stop(self):
        """Stop the analysis bot"""
        self.is_running = False
        logger.info("🛑 Professional Analysis Bot stopped")

# Global bot instance
analysis_bot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan management"""
    global analysis_bot
    # Startup sequence
    logger.info("🚀 Starting Professional Crypto Analysis Bot...")
    try:
        # Initialize bot
        analysis_bot = ProfessionalCryptoAnalysisBot()
        # Initialize Telegram if token provided
        telegram_ready = False
        if (analysis_bot.config.TELEGRAM_TOKEN and 
            analysis_bot.config.TELEGRAM_TOKEN != 'YOUR_TELEGRAM_BOT_TOKEN_HERE'):
            telegram_ready = await analysis_bot.telegram.initialize()
            if telegram_ready:
                await analysis_bot.telegram.start_webhook(analysis_bot.config.WEBHOOK_URL)
                logger.info("✅ Telegram integration active")
            else:
                logger.warning("⚠️ Telegram initialization failed - running without notifications")
        else:
            logger.warning("⚠️ No Telegram token provided - running in analysis-only mode")
        # Generate initial analysis
        logger.info("📊 Generating initial market analysis...")
        initial_report = await analysis_bot.generate_complete_analysis()
        if telegram_ready:
            await analysis_bot.telegram.send_analysis_report(initial_report)
        # Start automated analysis in background
        asyncio.create_task(analysis_bot.run_automated_analysis())
        logger.info("✅ Professional Analysis Bot fully operational")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    yield  # Application runs here
    # Shutdown sequence
    logger.info("🛑 Shutting down Professional Analysis Bot...")
    if analysis_bot:
        analysis_bot.stop()
        if hasattr(analysis_bot, 'telegram'):
            await analysis_bot.telegram.stop_webhook()

# FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title="Professional Crypto Analysis Bot",
    description="Institutional-grade cryptocurrency analysis with professional formatting",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check and bot status"""
    return {
        "status": "✅ Professional Crypto Analysis Bot Active",
        "description": "Institutional-grade cryptocurrency analysis",
        "timestamp": datetime.now().isoformat(),
        "bot_running": analysis_bot.is_running if analysis_bot else False,
        "last_analysis": analysis_bot.last_analysis_time.isoformat() if analysis_bot and analysis_bot.last_analysis_time else None,
        "telegram_enabled": analysis_bot.telegram.initialized if analysis_bot else False
    }

@app.get("/status")
async def detailed_status():
    """Detailed bot status"""
    if not analysis_bot:
        return {"error": "Bot not initialized"}
    return {
        "bot_status": "running" if analysis_bot.is_running else "stopped", 
        "primary_symbol": analysis_bot.config.DEFAULT_SYMBOL,
        "analysis_interval": f"{analysis_bot.config.ANALYSIS_INTERVAL} minutes",
        "supported_symbols": analysis_bot.config.SYMBOLS,
        "telegram_configured": analysis_bot.telegram.initialized,
        "last_analysis": analysis_bot.last_analysis_time.isoformat() if analysis_bot.last_analysis_time else "None",
        "next_analysis": f"~{60 - datetime.now().minute} minutes",
        "exchange": analysis_bot.config.EXCHANGE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/analyze/{symbol}")
async def manual_analysis(symbol: str):
    """Generate manual analysis for specific symbol"""
    if not analysis_bot:
        return {"error": "Bot not initialized"}
    try:
        # Validate symbol format
        symbol_formatted = symbol.upper()
        if '/' not in symbol_formatted:
            symbol_formatted = f"{symbol_formatted}/USDT"
        logger.info(f"📊 Manual analysis requested for {symbol_formatted}")
        report = await analysis_bot.manual_analysis(symbol_formatted)
        return {
            "symbol": symbol_formatted,
            "analysis": report,
            "timestamp": datetime.now().isoformat(),
            "type": "manual_request"
        }
    except Exception as e:
        logger.error(f"❌ Manual analysis failed: {e}")
        return {"error": f"Analysis failed: {str(e)}"}

@app.get("/analyze")
async def manual_analysis_default():
    """Generate manual analysis for default symbol (ETHUSDT)"""
    return await manual_analysis("ETHUSDT")

@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        update_data = await request.json()
        # Process Telegram update if needed
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"❌ Telegram webhook error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health_check():
    """Simple health check for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    import os
    # Get port from environment (required for Render)
    port = int(os.getenv('PORT', 8000))
    logger.info(f"🚀 Starting Professional Analysis Bot on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
