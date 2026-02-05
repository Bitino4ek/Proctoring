import os
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

# Настройки из Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
MY_CHAT_ID = os.getenv("CHAT_ID")

client = genai.Client(api_key=GEMINI_KEY)

# Веб-сервер для Render (чтобы не было Port Binding Error)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отвечаем только на сообщения от вашего CHAT_ID
    if str(update.message.chat_id) != str(MY_CHAT_ID): return

    try:
        file = await update.message.photo[-1].get_file()
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Запрос к Gemini
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=["Реши задачу на фото максимально кратко.", image]
        )
        await update.message.reply_text(f"✅ ОТВЕТ:\n{response.text}")
    except Exception as e:
        print(f"Ошибка ИИ: {e}")

if __name__ == '__main__':
    # Запуск заглушки порта в фоновом потока
    threading.Thread(target=run_server, daemon=True).start()
    
    # Запуск бота
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling(drop_pending_updates=True) # Игнорируем старые сообщения при запуске