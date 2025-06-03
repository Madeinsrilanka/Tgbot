import os
import re
import requests
import psutil
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import google.generativeai as genai

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
API_LINK = "https://www.dark-yasiya-api.site"
API_KEY = "yasiyalk"

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Messages
URL_PROMPT = "Give me movie url?"
INVALID_URL = "This Url Type is Invalid"
NOT_FOUND = "I can't find anything"
MOVIE_PROMPT = "Please give me movie or TV show name"
ERROR_MSG = "❗ error"

# Track bot start time (for uptime)
BOT_START_TIME = time.time()

# System Monitoring Functions
def get_system_ram():
    ram = psutil.virtual_memory()
    return f"{ram.used / (1024**3):.1f}GB / {ram.total / (1024**3):.1f}GB"

def get_system_storage():
    disk = psutil.disk_usage('/')
    return f"{disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB"

def get_system_uptime():
    return str(timedelta(seconds=time.time() - psutil.boot_time())).split('.')[0]

def get_bot_uptime():
    return str(timedelta(seconds=time.time() - BOT_START_TIME)).split('.')[0]

# Helper functions for movie bot
def format_number(num):
    return str(num).zfill(1)

async def fetch_api(endpoint, params):
    params['apikey'] = API_KEY
    response = requests.get(f"{API_LINK}{endpoint}", params=params)
    return response.json()

async def send_movie_details(update, context, movie_data, is_tv=False):
    if is_tv:
        text = f"""
📺 *Tv Show Name:* {movie_data['title']}
✨ *First Air Date:* {movie_data['first_air_date']}
🎐 *Last Air Date:* {movie_data['last_air_date']}
🎀 *Categories:* {movie_data['category']}
⭐ *TMDB RATING:* {movie_data['tmdbRate']}
🔮 *TMDB COUNT:* {movie_data['tmdbVoteCount']}
🎡 *Episode Count:* {movie_data['episode_count']}
"""
    else:
        cast = ', '.join([actor['name'] for actor in movie_data['cast']])
        text = f"""
🍟 *{movie_data['title']}*

🧿 Release Date: ➜ {movie_data['date']}
🌍 Country: ➜ {movie_data['country']}
⏱️ Duration: ➜ {movie_data['duration']}
🎀 Categories: ➜ {movie_data['category']}
⭐ IMDB: ➜ {movie_data['imdbRate']}
🤵‍♂️ Director: ➜ {movie_data['director']}
🕵️‍♂️ Cast: ➜ {cast}
"""
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=movie_data['mainImage'],
        caption=text,
        parse_mode='Markdown'
    )

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    user = update.message.from_user
    full_name = user.full_name or "there"
    
    welcome_msg = f"""
Hello, 👋 *{full_name}*. ♥️  

👏 Welcome to *Multi-Function Bot*  

•──────────────────────────•  
📜 *RAM* : {get_system_ram()}  
💾 *Storage* : {get_system_storage()}  
⏰ *System Uptime* : {get_system_uptime()}  
⏱ *Bot Uptime* : {get_bot_uptime()}  
🧠 *Gemini AI & Movie Download System*  
•──────────────────────────•  

Do you have any questions? Send a message or type /help.
    """
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
🔍 *Help Menu*:

*AI Functions:*
• Just send me a message to chat with Gemini AI

*Movie Functions:*
• Send a movie/TV show name to search
• /movies - Show movie commands help

*General Commands:*
• /start - Show welcome message
• /help - This menu
• /stats - Show system status

📝 *Examples*:
• "Explain quantum computing" (AI)
• "Avengers Endgame" (Movie)
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def movies_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show movie commands help"""
    help_text = """
🎬 *Movie Commands Help*:

• Just send a movie/TV show name to search
• The bot will show you results and options

📝 *Examples*:
• "Avengers Endgame"
• "Stranger Things season 1"
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send system stats"""
    stats_msg = f"""
🖥 *System Status*:

• RAM: {get_system_ram()}
• Storage: {get_system_storage()}
• System Uptime: {get_system_uptime()}
• Bot Uptime: {get_bot_uptime()}
"""
    await update.message.reply_text(stats_msg, parse_mode='Markdown')

# Message handlers
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all non-command messages with Gemini"""
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ Sorry, I encountered an error. Please try again.")

async def search_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle movie search requests"""
    query = update.message.text
    if not query:
        await update.message.reply_text(MOVIE_PROMPT)
        return
    
    try:
        result = await fetch_api("/private/sit1/sc1", {"text": query})
        if not result.get('result', {}).get('data'):
            await update.message.reply_text(NOT_FOUND)
            return
            
        movies = result['result']['data']
        keyboard = []
        
        text = "🔮 *MOVIE SEARCH RESULTS* 🔮\n\n📲 Input: *{query}*\n\n"
        
        for idx, movie in enumerate(movies, 1):
            title = re.sub(r'Sinhala Subtitles \| සිංහල උපසිරැසි සමඟ|Sinhala Subtitle \| සිංහල උපසිරැසි සමඟ', '', movie['title'])
            text += f"{format_number(idx)}. {title} | {movie['type']}\n"
            
            if movie['type'] == 'TV':
                callback_data = f"tv_{movie['link']}"
            else:
                callback_data = f"movie_{movie['link']}"
                
            keyboard.append([InlineKeyboardButton(f"Select {idx}", callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(ERROR_MSG)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("movie_"):
        url = data.split("_")[1]
        await handle_movie_selection(query, context, url)
    elif data.startswith("tv_"):
        url = data.split("_")[1]
        await handle_tv_selection(query, context, url)
    elif data.startswith("dl_"):
        # Handle download selection
        pass

async def handle_movie_selection(query, context, url):
    """Handle movie selection"""
    try:
        result = await fetch_api("/private/sit1/sc2", {"url": url})
        movie = result['result']['data']
        
        keyboard = [
            [InlineKeyboardButton("📽️ Download Movie", callback_data=f"dl_{url}")],
            [InlineKeyboardButton("ℹ️ Movie Details", callback_data=f"details_{url}")]
        ]
        
        text = f"""
🎬 *MOVIE DETAILS*

📽️ Title: {movie['title']}
🍟 Release Date: {movie['date']}
⏱ Duration: {movie['duration']}
"""
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=movie['mainImage'],
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Error: {e}")
        await query.edit_message_text(ERROR_MSG)

async def handle_tv_selection(query, context, url):
    """Handle TV show selection"""
    try:
        result = await fetch_api("/private/sit1/sc3", {"url": url})
        tv_show = result['result']['data']
        
        keyboard = []
        text = f"""
📺 *TV SHOW DETAILS*

📽️ Title: {tv_show['title']}
✨ First Air Date: {tv_show['first_air_date']}
🎐 Last Air Date: {tv_show['last_air_date']}
"""
        for idx, episode in enumerate(tv_show['episodes'], 1):
            text += f"\n{format_number(idx)}. {episode['number']} ({episode['name']})"
            keyboard.append([InlineKeyboardButton(
                f"Episode {episode['number']}", 
                callback_data=f"ep_{episode['link']}"
            )])
        
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=tv_show['mainImage'],
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Error: {e}")
        await query.edit_message_text(ERROR_MSG)

def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("movies", movies_help))

    # Message handlers
    # Default to AI handler unless it looks like a movie query
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex(r'^(/|https?://)'),
        handle_ai_message
    ))
    
    # Movie search handler for specific patterns
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(r'^(movie|film|tv show|season|episode|download)', re.IGNORECASE),
        search_movies
    ))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
