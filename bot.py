import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from dotenv import load_dotenv

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Клавиатура с тремя кнопками ---
inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔗 Курсро Тамошо кардан",
                url="https://www.youtube.com/watch?v=kTdFLbqT-2Y"
            )
        ],
        [
            InlineKeyboardButton(
                text="📞 Раками Телефон",
                callback_data="show_phone"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗨️ Менечер",
                url="https://t.me/Jannat_Abdullaeva_Admin"
            )
        ]
    ]
)

# --- Обработчик команды /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Подготавливаем фото
    photo = FSInputFile("photo.jpg")

    # Текст с иконками
    caption_text = (
        "🔥 *ЭРДАМ* 🔥\n\n"
        "5 қадами асосӣ барои ба даст овардани даромад дар Инстаграм.\n\n"
        "📘 Малумот дар бораи курси Маркетинг, Смм ва Бренди\n"
        "👤 Шахси Ватсап: wa.me/992200504437\n"
        "📞 Телефон: +992200504437\n\n"
        "🛠 *Техподдержка:* @Mustafo_IT\n"
        "❓ *Саволҳо оид ба курс:* @Jannat_Abdullaeva_Admin\n\n"
        "Хамеша дар хидмати шумо ҳастем! 🎉"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=inline_kb
    )

# --- Обработчик callback для кнопки "📞 Раками Телефон" ---
@dp.callback_query(lambda c: c.data == "show_phone")
async def show_phone(callback: types.CallbackQuery):
    await callback.answer()  # убираем "часики"
    await callback.message.answer(
        "📞 *Наш телефон:* +992200504437\n"
        "💬 *WhatsApp:* [написать](https://wa.me/992200504437)",
        parse_mode="Markdown"
    )

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
