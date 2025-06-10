import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FATHER_BOT_URL = os.getenv('FATHER_BOT_URL', '').strip()  # Удаляем пробелы

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не задан! Добавьте его в .env файл.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот omniscient. Отправь мне сообщение, и я отвечу.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Получено сообщение: {user_message}")

    # Если FATHER_BOT_URL не задан, просто отвечаем эхом
    if not FATHER_BOT_URL:
        await update.message.reply_text(f"Вы сказали: {user_message}")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                FATHER_BOT_URL,
                json={"prompt": user_message},
                timeout=5
            ) as response:
                # Проверяем статус ответа
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {response.status} - {error_text}")
                    await update.message.reply_text("Сервер вернул ошибку. Попробуйте позже.")
                    return

                # Пытаемся разобрать JSON
                try:
                    data = await response.json()
                    if "response" in data:
                        await update.message.reply_text(data["response"])
                    else:
                        logger.error(f"Неожиданный формат ответа: {data}")
                        await update.message.reply_text("Не получилось обработать ответ сервера.")
                except ValueError as e:
                    logger.error(f"Ошибка парсинга JSON: {e}")
                    await update.message.reply_text("Ошибка в данных сервера.")

    except aiohttp.ClientError as e:
        logger.error(f"Ошибка подключения: {str(e)}")
        await update.message.reply_text("Не удалось подключиться к серверу. Проверьте интернет.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {str(e)}")
        await update.message.reply_text("Произошла внутренняя ошибка.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.run_polling()