import os
import io
import requests
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

# --- НАСТРОЙКИ (через переменные окружения или просто впиши) ---
TOKEN = "ТВОЙ_ТОКЕН_ТЕЛЕГРАМ"
GEMINI_KEY = "ТВОЙ_КЛЮЧ_GEMINI"

# Инициализация Gemini
client = genai.Client(api_key=GEMINI_KEY)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 1. Скачиваем фото из Telegram в память
        file = await update.message.photo[-1].get_file()
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        # 2. Отправляем в Gemini (облако само достучится до Google)
        prompt = "Реши задание на картинке. Напиши только краткий ответ и логику."
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[prompt, image]
        )
        
        # 3. Присылаем ответ обратно
        await update.message.reply_text(f"✅ РЕШЕНИЕ:\n{response.text}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

if name == 'main':
    # Запуск бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Бот запущен в облаке...")
    app.run_polling()