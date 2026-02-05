import os
import io
import asyncio
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
MY_CHAT_ID = os.getenv("CHAT_ID")

# Инициализация Gemini
client = genai.Client(api_key=GEMINI_KEY)

# 1. Заглушка для Render (чтобы не было ошибки Port Binding)
def run_health_check_server():
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.chat_id) != str(MY_CHAT_ID):
        return
    try:
        file = await update.message.photo[-1].get_file()
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        # ИСПОЛЬЗУЕМ ОБНОВЛЕННОЕ ИМЯ МОДЕЛИ
        response = client.models.generate_content(
            model="gemini-1.5-flash-002", 
            contents=["Реши задание на картинке кратко.", image]
        )
        await update.message.reply_text(f"✅ ОТВЕТ:\n{response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

if name == 'main':
    # Запускаем веб-заглушку в отдельном потоке
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    # Запускаем бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🚀 Бот запущен...")
    app.run_polling()