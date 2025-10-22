import os
import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Print Python version and environment info
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Environment variables count: {len(os.environ)}")

# DEBUG: Print all environment variable names
print("\n🔍 All environment variable names:")
for key in sorted(os.environ.keys()):
    if 'TOKEN' in key or 'KEY' in key or 'TELEGRAM' in key:
        value = os.environ[key]
        print(f"  {key} = {value[:30]}..." if len(value) > 30 else f"  {key} = {value}")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment - try multiple methods
print("\n🔑 Attempting to load TELEGRAM_BOT_TOKEN...")

TELEGRAM_TOKEN = None

# Method 1: Direct os.environ
if 'TELEGRAM_BOT_TOKEN' in os.environ:
    TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    print(f"✅ Method 1 (os.environ) succeeded: {TELEGRAM_TOKEN[:20]}...")

# Method 2: os.environ.get
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    if TELEGRAM_TOKEN:
        print(f"✅ Method 2 (os.environ.get) succeeded: {TELEGRAM_TOKEN[:20]}...")

# Method 3: os.getenv
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if TELEGRAM_TOKEN:
        print(f"✅ Method 3 (os.getenv) succeeded: {TELEGRAM_TOKEN[:20]}...")

# Final check
if not TELEGRAM_TOKEN:
    print("\n" + "="*60)
    print("❌ CRITICAL ERROR: TELEGRAM_BOT_TOKEN not found!")
    print("="*60)
    print("\n📋 Troubleshooting steps:")
    print("1. Go to Render Dashboard → Your Service → Environment")
    print("2. Check if 'TELEGRAM_BOT_TOKEN' exists")
    print("3. Key must be EXACTLY: TELEGRAM_BOT_TOKEN (case-sensitive)")
    print("4. Value must be your full token")
    print("5. Click 'Save Changes'")
    print("6. Manually deploy again")
    print("\n🔍 Available environment variables with 'T' or 'K':")
    for key in os.environ.keys():
        if any(x in key.upper() for x in ['T', 'K']):
            print(f"   - {key}")
    sys.exit(1)

print(f"\n✅ Token loaded successfully!")
print(f"   Length: {len(TELEGRAM_TOKEN)}")
print(f"   Preview: {TELEGRAM_TOKEN[:25]}...")

# Optional: OpenAI
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    print(f"✅ OpenAI key found: {OPENAI_API_KEY[:20]}...")
else:
    print("⚠️  OpenAI key not found (AI chat will not work)")

# User data
user_data = {}

# Languages
LANGUAGES = {
    'uz': '🇺🇿 O\'zbekcha',
    'en': '🇬🇧 English',
    'ru': '🇷🇺 Русский',
    'tr': '🇹🇷 Türkçe',
    'ar': '🇸🇦 العربية',
    'es': '🇪🇸 Español',
}

def get_main_keyboard():
    """Main menu keyboard"""
    keyboard = [
        [KeyboardButton('🌍 Tarjima'), KeyboardButton('⚙️ Sozlamalar')],
        [KeyboardButton('ℹ️ Yordam')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_language_keyboard():
    """Language selection keyboard"""
    keyboard = []
    langs = list(LANGUAGES.items())
    for i in range(0, len(langs), 2):
        row = []
        row.append(InlineKeyboardButton(langs[i][1], callback_data=f'lang_{langs[i][0]}'))
        if i + 1 < len(langs):
            row.append(InlineKeyboardButton(langs[i+1][1], callback_data=f'lang_{langs[i+1][0]}'))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {
            'target_language': 'en',
            'mode': 'translate'
        }
    
    welcome_text = """
🤖 Assalomu aleykum! Men tarjimon botman!

✨ Imkoniyatlar:
• 🌍 Matnlarni tarjima qilish
• ⚙️ Tilni tanlash
• 🆓 Bepul xizmat

Matn yuboring, tarjima qilaman! 🚀
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate text"""
    user_id = update.effective_user.id
    text = update.message.text
    target_lang = user_data.get(user_id, {}).get('target_language', 'en')
    
    try:
        from deep_translator import GoogleTranslator
        
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        response = f"🌍 Tarjima:\n\n{translated}"
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text("❌ Tarjima xatoligi. Qaytadan urinib ko'ring.")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings"""
    await update.message.reply_text(
        "⚙️ Tarjima tilini tanlang:",
        reply_markup=get_language_keyboard()
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang_code = query.data.split('_')[1]
    
    if user_id not in user_data:
        user_data[user_id] = {'target_language': 'en', 'mode': 'translate'}
    
    user_data[user_id]['target_language'] = lang_code
    lang_name = LANGUAGES.get(lang_code, 'Unknown')
    
    await query.edit_message_text(
        f"✅ Til o'rnatildi: {lang_name}\n\nMatn yuboring!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help"""
    help_text = """
📖 Qo'llanma:

1️⃣ 🌍 Tarjima - Matn yuboring
2️⃣ ⚙️ Sozlamalar - Tilni tanlang
3️⃣ ℹ️ Yordam - Bu xabar

Faqat matn yuboring, avtomatik tarjima bo'ladi! 😊
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_data:
        user_data[user_id] = {'target_language': 'en', 'mode': 'translate'}
    
    if text == '🌍 Tarjima':
        await update.message.reply_text("Matn yuboring, tarjima qilaman!")
    elif text == '⚙️ Sozlamalar':
        await settings(update, context)
    elif text == 'ℹ️ Yordam':
        await help_command(update, context)
    else:
        await translate_text(update, context)

def main():
    """Start the bot"""
    
    print("\n" + "="*60)
    print("🚀 Starting Telegram Bot...")
    print("="*60)
    
    try:
        # Create application
        print(f"Creating Telegram Application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        print("✅ Application created successfully")
        
        # Add handlers
        print("Adding handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
        print("✅ Handlers added successfully")
        
        # Start bot
        print("\n✅ Bot ishga tushdi!")
        print("="*60)
        logger.info("🤖 Bot running... Press Ctrl+C to stop")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
