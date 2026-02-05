import os
import io
import requests
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

# --- ПОЛУЧЕНИЕ НАСТРОЕК ИЗ ОБЛАКА ---
# Эти команды заставляют скрипт искать значения в настройках Render
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
MY_CHAT_ID = os.getenv("CHAT_ID")

# Инициализация Gemini
client = genai.Client(api_key=GEMINI_KEY)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка: бот будет отвечать только вам
    if str(update.message.chat_id) != str(MY_CHAT_ID):
        return

    try:
        file = await update.message.photo[-1].get_file()
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        print("🤖 Обработка фото в облаке...")
        prompt = "Реши задание на картинке. Напиши кратко ответ."
        
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[prompt, image]
        )
        
        await update.message.reply_text(f"✅ РЕШЕНИЕ:\n{response.text}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка ИИ: {str(e)}")

if name == 'main':
    if not TOKEN or not MY_CHAT_ID:
        print("Ошибка: Переменные окружения не настроены!")
    else:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        print("🚀 Бот запущен на сервере Render...")
        app.run_polling()