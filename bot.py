import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from dotenv import load_dotenv

# Загружаем токен из .env файла
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Клавиатуры ---

# Inline-кнопка "Старт" (вызывает callback)
start_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Старт", callback_data="start_action")]
    ]
)

# Клавиатура с ссылкой (можно добавить после отправки фото)
link_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Перейти по ссылке", url="https://youtu.be/19KAG5S5RWg")]
    ]
)

# --- Обработчики ---

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋\nНажми кнопку «Старт», чтобы получить материал:",
        reply_markup=start_inline_kb
    )

# Обработчик нажатия на inline-кнопку "Старт"
@dp.callback_query(lambda c: c.data == "start_action")
async def process_start_callback(callback: types.CallbackQuery):
    # Отвечаем на callback, чтобы убрать "часики"
    await callback.answer()

    # Подготавливаем фото (замени "photo.jpg" на свой файл)
    photo = FSInputFile("photo.jpg")

    # Текст сообщения
    caption_text = (
        "🔥 *Вот твой бонус!*\n\n"
        "📘 *2025-йил Запусклардаги ўсиш нуқталари*\n\n"
        "Стратегия, хатолар ва эътибор бериш керак бўлган жиҳатлар.\n\n"
        "👇 Видео дарсни кўриш учун тугмани босинг:"
    )

    # Отправляем фото с текстом и кнопкой-ссылкой
    await callback.message.answer_photo(
        photo=photo,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=link_button
    )

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
