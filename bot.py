import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

USERS_FILE = "users.json"

# --- Работа с пользователями ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users), f)

users = load_users()

def add_user(user_id):
    if user_id not in users:
        users.add(user_id)
        save_users(users)

# --- Состояния для создания рассылки ---
class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_video_link = State()
    waiting_for_time = State()
    confirming = State()

# --- Клавиатуры ---
# Основная клавиатура бота (как была)
main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📞 Раками Телефон", callback_data="show_phone")],
        [InlineKeyboardButton(text="🗨️ Ватсап", url="https://wa.me/992200504437")]
    ]
)

# Админ-панель
admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 Создать рассылку", callback_data="admin_new_broadcast")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
    ]
)

# Клавиатура выбора времени
time_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Сейчас", callback_data="time_now")],
        [InlineKeyboardButton(text="⏰ Через 1 час", callback_data="time_1h")],
        [InlineKeyboardButton(text="⏰ Через 3 часа", callback_data="time_3h")],
        [InlineKeyboardButton(text="⌨️ Ввести время", callback_data="time_custom")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
    ]
)

# Клавиатура подтверждения
confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="confirm_send")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="confirm_edit")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
    ]
)

# --- Старт бота ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user.id)   # запоминаем пользователя

    photo = FSInputFile("photo.jpg")
    user_name = message.from_user.first_name

    caption_text = (
        f"👋 Салом {user_name}!\n\n"
        "📚 Ба шумо дарси «5 қадам барои даромад дар Инстаграм» пешкаш карда мешавад!\n\n"
        "🎯 Дар ин дарс шумо чиро меомузед:\n"
        "- Чӣ тавр стратегия тартиб додан?\n"
        "- Дар бозор чӣ хатоҳо вуҷуд дорад?\n"
        "- Ба чӣ чизҳо таваҷҷӯҳ кардан лозим?\n\n"
        "📘 Маълумот дар бораи курси Маркетинг, СММ ва Бренд\n\n"
        "🎥 https://www.youtube.com/watch?v=kTdFLbqT-2Y\n\n"
        "📞 Раками телефон: +992200504437"
    )

    # Клавиатура только с Ватсап
    whatsapp_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗨️ Ватсап", url="https://wa.me/992200504437")]
        ]
    )

    await message.answer_photo(
        photo=photo,
        caption=caption_text,
        parse_mode="HTML",
        reply_markup=whatsapp_kb
    )
# --- Админ-панель ---
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer("🔧 Админ-панель:", reply_markup=admin_kb)

# --- Создание новой рассылки ---
@dp.callback_query(lambda c: c.data == "admin_new_broadcast")
async def new_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа")
        return
    await callback.answer()
    await state.set_state(BroadcastStates.waiting_for_text)
    await callback.message.answer(
        "✍️ Введите текст сообщения для рассылки.\n"
        "Можно использовать HTML-разметку (например, <b>жирный</b>).\n"
        "Чтобы отменить — /cancel"
    )

# --- Обработка текста ---
@dp.message(BroadcastStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(BroadcastStates.waiting_for_photo)
    await message.answer(
        "📸 Теперь отправьте фото (как файл или ссылку).\n"
        "Если фото не нужно — отправьте слово 'пропустить'."
    )

# --- Обработка фото ---
@dp.message(BroadcastStates.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    photo = None
    if message.photo:
        # Берём самое большое качество
        photo = message.photo[-1].file_id
    elif message.text and message.text.strip().lower() == "пропустить":
        photo = None
    elif message.text and (message.text.startswith("http://") or message.text.startswith("https://")):
        # Можно сохранить как ссылку, но для отправки лучше использовать file_id
        # Здесь просто сохраним как ссылку, при отправке будем использовать как URL
        photo = message.text
    else:
        await message.answer("Пожалуйста, отправьте фото или напишите 'пропустить'.")
        return

    await state.update_data(photo=photo)
    await state.set_state(BroadcastStates.waiting_for_video_link)
    await message.answer(
        "🎥 Введите ссылку на видео (или отправьте слово 'пропустить').\n"
        "Ссылка будет добавлена как кнопка под сообщением."
    )

# --- Обработка ссылки на видео ---
@dp.message(BroadcastStates.waiting_for_video_link)
async def process_video_link(message: types.Message, state: FSMContext):
    video_link = None
    if message.text and message.text.strip().lower() != "пропустить":
        if message.text.startswith("http"):
            video_link = message.text.strip()
        else:
            await message.answer("Это не похоже на ссылку. Введите корректную ссылку или 'пропустить'.")
            return
    await state.update_data(video_link=video_link)
    await state.set_state(BroadcastStates.waiting_for_time)
    await message.answer("⏰ Выберите время отправки:", reply_markup=time_kb)

# --- Обработка выбора времени ---
@dp.callback_query(lambda c: c.data.startswith("time_"))
async def process_time_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = callback.data
    now = datetime.now()
    delay_seconds = 0

    if data == "time_now":
        delay_seconds = 0
    elif data == "time_1h":
        delay_seconds = 3600
    elif data == "time_3h":
        delay_seconds = 10800
    elif data == "time_custom":
        await state.set_state(BroadcastStates.waiting_for_time)
        await callback.message.answer(
            "Введите время в формате:\n"
            "• `+2` — через 2 часа\n"
            "• `14:30` — сегодня в 14:30\n"
            "• `14:30 25.12` — в указанную дату\n\n"
            "Пример: `+1.5` или `09:00`",
            parse_mode="Markdown"
        )
        return
    else:
        await callback.message.answer("Неизвестный выбор.")
        return

    await state.update_data(delay_seconds=delay_seconds)
    await show_preview(callback.message, state)

# --- Обработка ручного ввода времени ---
@dp.message(BroadcastStates.waiting_for_time)
async def process_custom_time(message: types.Message, state: FSMContext):
    user_input = message.text.strip()
    delay_seconds = parse_time(user_input)
    if delay_seconds is None:
        await message.answer("❌ Неверный формат. Попробуйте ещё раз или /cancel")
        return
    if delay_seconds <= 0:
        await message.answer("❌ Время должно быть в будущем.")
        return
    await state.update_data(delay_seconds=delay_seconds)
    await show_preview(message, state)

def parse_time(user_input):
    """Парсит время, возвращает секунды задержки или None"""
    now = datetime.now()
    # +часы
    if user_input.startswith('+'):
        try:
            hours = float(user_input[1:])
            return int(hours * 3600)
        except:
            return None
    # HH:MM
    if re.match(r'^\d{1,2}:\d{2}$', user_input):
        try:
            target_time = datetime.strptime(user_input, "%H:%M").time()
            target = datetime.combine(now.date(), target_time)
            if target < now:
                target += timedelta(days=1)
            return (target - now).total_seconds()
        except:
            return None
    # HH:MM DD.MM
    if re.match(r'^\d{1,2}:\d{2}\s+\d{1,2}\.\d{2}$', user_input):
        try:
            time_part, date_part = user_input.split()
            target_time = datetime.strptime(time_part, "%H:%M").time()
            target_date = datetime.strptime(date_part, "%d.%m").date()
            year = now.year
            target = datetime.combine(target_date.replace(year=year), target_time)
            if target < now:
                target = datetime.combine(target_date.replace(year=year+1), target_time)
            return (target - now).total_seconds()
        except:
            return None
    return None

# --- Показ предпросмотра ---
async def show_preview(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    photo = data.get("photo")
    video_link = data.get("video_link")
    delay = data.get("delay_seconds", 0)

    # Формируем клавиатуру, если есть видео
    reply_markup = None
    if video_link:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Смотреть видео", url=video_link)]
        ])
        reply_markup = kb

    preview_text = f"📝 <b>Предпросмотр рассылки</b>\n\n{text}"
    if delay:
        hours = delay // 3600
        minutes = (delay % 3600) // 60
        preview_text += f"\n\n⏱️ <i>Отправка через {hours} ч. {minutes} мин.</i>"

    # Отправляем предпросмотр (с фото, если есть)
    if photo:
        if isinstance(photo, str) and (photo.startswith("http") or photo.startswith("agc")):
            # Это может быть file_id или URL
            await message.answer_photo(photo=photo, caption=preview_text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            # Если это file_id, используем его
            await message.answer_photo(photo=photo, caption=preview_text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await message.answer(preview_text, parse_mode="HTML", reply_markup=reply_markup)

    await state.set_state(BroadcastStates.confirming)
    await message.answer("✅ Подтвердите отправку:", reply_markup=confirm_kb)

# --- Подтверждение отправки ---
@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_broadcast(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа")
        return
    await callback.answer()
    if callback.data == "confirm_edit":
        await state.set_state(BroadcastStates.waiting_for_text)
        await callback.message.answer("✍️ Редактируйте текст (можно начать заново):")
        return
    elif callback.data == "confirm_send":
        data = await state.get_data()
        delay = data.get("delay_seconds", 0)
        if delay == 0:
            await callback.message.answer("🚀 Отправляю сейчас...")
            await send_broadcast(data)
            await callback.message.answer("✅ Готово.")
        else:
            await callback.message.answer(f"⏳ Отправка запланирована через {delay//3600} ч. {(delay%3600)//60} мин.")
            asyncio.create_task(schedule_broadcast(data, delay, callback.message.chat.id))
        await state.clear()
    elif callback.data == "admin_cancel":
        await state.clear()
        await callback.message.answer("❌ Отменено.")

# --- Функция отправки рассылки ---
async def send_broadcast(data: dict):
    text = data.get("text", "")
    photo = data.get("photo")
    video_link = data.get("video_link")
    reply_markup = None
    if video_link:
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎥 Смотреть видео", url=video_link)]
        ])

    for user_id in users:
        try:
            if photo:
                await bot.send_photo(user_id, photo=photo, caption=text, parse_mode="HTML", reply_markup=reply_markup)
            else:
                await bot.send_message(user_id, text, parse_mode="HTML", reply_markup=reply_markup)
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.error(f"Ошибка отправки {user_id}: {e}")

async def schedule_broadcast(data, delay, admin_chat_id):
    await asyncio.sleep(delay)
    await bot.send_message(admin_chat_id, "🔔 Начинаю запланированную рассылку...")
    await send_broadcast(data)
    await bot.send_message(admin_chat_id, "✅ Запланированная рассылка завершена.")

# --- Статистика ---
@dp.callback_query(lambda c: c.data == "admin_stats")
async def show_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа")
        return
    await callback.answer()
    await callback.message.answer(f"📊 Всего пользователей: {len(users)}")

# --- Отмена /cancel ---
@dp.message(Command("cancel"))
async def cancel_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.")

# --- Запуск ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
