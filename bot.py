import os
import psutil
import time
from datetime import timedelta
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Configuration (use environment variables)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# System Monitoring Functions
def get_system_ram():
    ram = psutil.virtual_memory()
    return f"{ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB"

def get_system_storage():
    disk = psutil.disk_usage('/')
    return f"{disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB"

def get_system_uptime():
    return str(timedelta(seconds=time.time() - psutil.boot_time())).split('.')[0]

def get_bot_uptime(start_time):
    return str(timedelta(seconds=time.time() - start_time)).split('.')[0]

# Track bot start time (for uptime)
BOT_START_TIME = time.time()

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a personalized welcome message"""
    user = update.message.from_user
    full_name = user.full_name or "there"
    
    welcome_message = f"""
Hello, 👋 *{full_name}*. ♥️  

👏 Welcome to *Gemma 3 Telegram*  

•──────────────────────────•  
📜 *RAM* : {get_system_ram()}  
💾 *Storage* : {get_system_storage()}  
⏰ *System Uptime* : {get_system_uptime()}  
⏱ *Bot Uptime* : {get_bot_uptime(BOT_START_TIME)}  
🧠 *Gemma 3*  
🧸 *Shafeer Cassim*  
•──────────────────────────•  

Do you have any questions? Send a message or type /help.
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
🔍 *Help Menu*:

• Just send me a message to chat with Gemini AI
• /start - Show welcome message
• /help - This menu
• /stats - Show system status

📝 *Examples*:
• "Explain quantum computing"
• "Write a poem about AI"
"""
    await update.message.reply_text(help_text, parse_mode=telegram.constants.ParseMode.MARKDOWN)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send system stats"""
    stats_msg = f"""
🖥 *System Status*:

• RAM: {get_system_ram()}
• Storage: {get_system_storage()}
• System Uptime: {get_system_uptime()}
• Bot Uptime: {get_bot_uptime(BOT_START_TIME)}
"""
    await update.message.reply_text(stats_msg, parse_mode=telegram.constants.ParseMode.MARKDOWN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all non-command messages with Gemini"""
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ Sorry, I encountered an error. Please try again.")

def main():
    """Start the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
