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

# --- Клавиатура с двумя кнопками ---
inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📞 Раками Телефон",
                callback_data="show_phone"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗨️ Ватсап",
                url="https://wa.me/992200504437"
            )
        ]
    ]
)

# --- Обработчик команды /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    photo = FSInputFile("photo.jpg")
    user_name = message.from_user.first_name

    caption_text = (
        f"👋 Салом {user_name} !\n\n"
        "📚 Ба шумо дарси «5 қадам барои даромад дар Инстаграм» пешкаш карда мешавад!\n\n"
        "🎯 Дар ин дарс муҳокима мешавад:\n"
        "- Чӣ тавр стратегия тартиб додан?\n"
        "- Дар бозор чӣ хатоҳо вуҷуд дорад?\n"
        "- Ба чӣ чизҳо таваҷҷӯҳ кардан лозим?\n\n"
        "📘 Маълумот дар бораи курси Маркетинг, СММ ва Бренд\n\n"
        "🎥 https://www.youtube.com/watch?v=kTdFLbqT-2Y"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption_text,
        parse_mode="HTML",
        reply_markup=inline_kb
    )

# --- Обработчик callback для кнопки "📞 Раками Телефон" ---
@dp.callback_query(lambda c: c.data == "show_phone")
async def show_phone(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📞 <b>Раками телефон:</b> +992200504437",
        parse_mode="HTML"
    )

# --- Запуск ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
