import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from dotenv import load_dotenv

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Клавиатуры ---

# Главная reply-клавиатура (меню)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 О курсе")],
        [KeyboardButton(text="📞 Контакты")],
        [KeyboardButton(text="🎥 Видео-урок")]
    ],
    resize_keyboard=True,          # Подгоняет размер под экран
    one_time_keyboard=False        # Клавиатура остаётся после нажатия
)

# Inline-кнопки для видео (ссылка + связаться)
video_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Смотреть видео", url="https://www.youtube.com/watch?v=kTdFLbqT-2Y")],
        [InlineKeyboardButton(text="📞 Связаться", callback_data="show_contacts")]
    ]
)

# Inline-кнопки для контактов (можно позвонить/написать)
contacts_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📞 Позвонить", url="tel:+992200504437")],
        [InlineKeyboardButton(text="💬 Написать в WhatsApp", url="https://wa.me/992200504437")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_menu")]
    ]
)

# Inline-кнопка для возврата в меню
back_to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_menu")]
    ]
)

# --- Обработчики команд ---

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Я бот образовательного центра. Выберите интересующий вас раздел:",
        reply_markup=main_menu_kb
    )

# Команда /help (справка)
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 *Как пользоваться ботом:*\n\n"
        "• Нажмите кнопку *«📚 О курсе»*, чтобы узнать о программе.\n"
        "• Нажмите *«📞 Контакты»*, чтобы связаться с нами.\n"
        "• Нажмите *«🎥 Видео-урок»*, чтобы получить бесплатный урок.\n\n"
        "Если возникли вопросы, пишите в WhatsApp или звоните — мы на связи!"
    )
    await message.answer(help_text, parse_mode="Markdown")

# --- Обработчики кнопок главного меню ---

# Кнопка "О курсе"
@dp.message(lambda msg: msg.text == "📚 О курсе")
async def about_course(message: types.Message):
    course_text = (
        "🎓 *О курсе «Маркетинг, SMM и Брендинг»*\n\n"
        "Курс разработан для тех, кто хочет освоить профессию "
        "SMM-специалиста и научиться продвигать бренды в Instagram.\n\n"
        "📌 *Программа включает:*\n"
        "• Стратегия продвижения\n"
        "• Создание контента\n"
        "• Таргетированная реклама\n"
        "• Работа с блогерами\n"
        "• Аналитика и отчёты\n\n"
        "По окончании вы получаете сертификат и помощь в трудоустройстве.\n\n"
        "Для записи на курс используйте кнопку «📞 Контакты» 👇"
    )
    await message.answer(course_text, parse_mode="Markdown", reply_markup=back_to_menu_kb)

# Кнопка "Контакты"
@dp.message(lambda msg: msg.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    contacts_text = (
        "📱 *Свяжитесь с нами:*\n\n"
        "• Телефон: +992 200 50 44 37\n"
        "• WhatsApp: wa.me/992200504437\n\n"
        "Напишите или позвоните — мы ответим на все вопросы!"
    )
    await message.answer(contacts_text, parse_mode="Markdown", reply_markup=contacts_inline_kb)

# Кнопка "Видео-урок"
@dp.message(lambda msg: msg.text == "🎥 Видео-урок")
async def send_video_lesson(message: types.Message):
    photo = FSInputFile("photo.jpg")  # Убедитесь, что файл существует
    caption_text = (
        "🎬 *Бесплатный видео-урок*\n\n"
        "5 қадами асосӣ барои ба даст овардани даромад дар Инстаграм.\n\n"
        "Малумот дар бораи курси Маркетинг, Смм ва Бренди.\n"
        "Шахси Ватсап: wa.me/992200504437\n"
        "📞 +992200504437"
    )
    await message.answer_photo(
        photo=photo,
        caption=caption_text,
        parse_mode="Markdown",
        reply_markup=video_inline_kb
    )

# --- Обработчики callback-запросов (для inline-кнопок) ---

# Показать контакты по callback (используется из видео)
@dp.callback_query(lambda c: c.data == "show_contacts")
async def inline_show_contacts(callback: types.CallbackQuery):
    await callback.answer()
    contacts_text = (
        "📱 *Свяжитесь с нами:*\n\n"
        "• Телефон: +992 200 50 44 37\n"
        "• WhatsApp: wa.me/992200504437"
    )
    await callback.message.answer(contacts_text, parse_mode="Markdown", reply_markup=contacts_inline_kb)

# Вернуться в главное меню
@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu_kb
    )
    # Удаляем сообщение с инлайн-кнопками, чтобы не захламлять чат
    await callback.message.delete()

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
