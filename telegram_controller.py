"""
Telegram controller for professional crypto analysis reports
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisTelegramController:
    def __init__(self, config):
        self.config = config
        self.application = None
        self.initialized = False

    async def initialize(self):
        """Initialize Telegram Application"""
        try:
            if not self.config.TELEGRAM_TOKEN or self.config.TELEGRAM_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
                logger.warning("❌ No valid Telegram token provided")
                return False

            self.application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()

            # Add command handlers  
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("help", self.help_command))

            await self.application.initialize()
            self.initialized = True
            logger.info("✅ Telegram Application initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing Telegram: {e}")
            return False

    async def start_webhook(self, webhook_url: str):
        """Start webhook for deployment"""
        if not self.initialized:
            if not await self.initialize():
                return False

        try:
            await self.application.bot.set_webhook(url=f"{webhook_url}/telegram")
            await self.application.start()
            logger.info("✅ Telegram webhook started")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting webhook: {e}")
            return False

    async def stop_webhook(self):
        """Stop webhook"""
        try:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Telegram webhook stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping webhook: {e}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🚀 **Professional Crypto Analysis Bot**

**📊 Features:**
• **Institutional-grade** market analysis
• **Multi-timeframe** technical analysis  
• **Professional formatting** like top funds
• **Risk management** guidelines
• **Real-time** market monitoring

**📈 Available Commands:**
/analyze - Generate complete market analysis
/status - Bot operational status
/help - Command guide

**🎯 Supported Assets:**
• ETHUSDT (primary)
• BTCUSDT  
• SOLUSDT

**⚡ Analysis includes:**
• Technical indicators (RSI, MACD, OBV)
• Support/Resistance levels
• Trade entry/exit levels
• Risk management guidelines
• Market sentiment scoring

**Ready to receive professional-grade analysis!** 📊
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_msg = """
✅ **Analysis Bot Status**

🤖 **Status:** Active & Monitoring
📊 **Primary Asset:** ETHUSDT
⏰ **Analysis Frequency:** Every 60 minutes
🔄 **Last Update:** {time}
📡 **Data Source:** Binance (Real-time)

🎯 **Active Features:**
• Multi-timeframe analysis (15m, 1h, 4h, 1d)
• Professional report formatting
• Risk management calculations
• Sentiment scoring algorithm

**📈 Next analysis in ~{next} minutes**
        """.format(
            time=datetime.now().strftime('%H:%M:%S %Z'),
            next=60 - datetime.now().minute
        )
        await update.message.reply_text(status_msg, parse_mode='Markdown')

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        await update.message.reply_text(
            "📊 **Generating professional analysis...**\n⏱️ Please wait 10-15 seconds",
            parse_mode='Markdown'
        )
        # Trigger analysis generation would happen here

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
📚 **Professional Analysis Bot - Command Guide**

**🔄 Analysis Commands:**
/analyze - Generate complete technical analysis
/status - Check bot operational status

**📊 What You Get:**
• **Anchor Candle** - Latest completed candle OHLC
• **Trading Matrix** - Entry/SL/TP for intraday & swing  
• **Key Levels** - Support/resistance zones
• **Technical Signals** - RSI, MACD, OBV analysis
• **Sentiment Scores** - Quantified market sentiment
• **Risk Management** - Professional guidelines

**⚡ Analysis Features:**
• **Production-grade formatting** (like institutional reports)
• **Multi-timeframe confluence** (15m to 1d)
• **Precise entry/exit levels** with R:R ratios
• **Volume-based confirmation** signals
• **Dynamic risk management** guidelines

**🎯 Report Updates:**
• Automatic analysis every 60 minutes
• Manual analysis via /analyze command
• Real-time price alerts for key levels

**📈 Professional-grade analysis at your fingertips!**
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')

    async def send_analysis_report(self, report: str):
        """Send professional analysis report"""
        if not self.initialized or not self.config.TELEGRAM_CHAT_ID:
            logger.warning("❌ Cannot send report - Telegram not configured")
            return False

        try:
            # Split long reports if needed (Telegram has 4096 char limit)
            if len(report) > 4000:
                parts = self._split_report(report)
                for i, part in enumerate(parts):
                    await self.application.bot.send_message(
                        chat_id=self.config.TELEGRAM_CHAT_ID,
                        text=part,
                        parse_mode='Markdown'
                    )
                    if i < len(parts) - 1:  # Add delay between parts
                        await asyncio.sleep(1)
            else:
                await self.application.bot.send_message(
                    chat_id=self.config.TELEGRAM_CHAT_ID,
                    text=report,
                    parse_mode='Markdown'
                )

            logger.info("✅ Analysis report sent successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending analysis report: {e}")
            return False

    def _split_report(self, report: str, max_length: int = 4000) -> list:
        """Split long reports into multiple messages"""
        lines = report.split('\n')
        parts = []
        current_part = ""

        for line in lines:
            if len(current_part + line + '\n') > max_length:
                if current_part:
                    parts.append(current_part.strip())
                current_part = line + '\n'
            else:
                current_part += line + '\n'

        if current_part:
            parts.append(current_part.strip())

        return parts
