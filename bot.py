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

# --- Клавиатура с ссылкой (обновлена) ---
link_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="🔗 Перейти по ссылке",
            url="https://www.youtube.com/watch?v=kTdFLbqT-2Y"
        )]
    ]
)

# --- Обработчики ---

# Команда /start — сразу отправляем фото с текстом и кнопкой
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    photo = FSInputFile("photo.jpg")  # фото должно лежать в папке с ботом

    caption_text = (
        "5 қадами асосӣ барои ба даст овардани даромад дар Инстаграм.\n\n"
        "Малумот дар бораи курси Маркетинг, Смм ва Бренди\n"
        "Шахси\n"
        "Ватсап\n"
        "wa.me/992200504437\n\n"
        "📞 +992200504437"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption_text,
        reply_markup=link_button
    )

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
