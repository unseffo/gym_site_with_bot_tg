import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ParseMode
from aiogram.dispatcher import filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import pymysql.cursors
from aiogram import executor
from aiogram.utils.exceptions import Unauthorized

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Токен вашого бота
API_TOKEN = ''

# Айді адміна (замініть на свій)
ADMIN_ID = ''

# Налаштування підключення до бази даних
DB_CONFIG = {
    'host': '',
    'user': '',
    'password': '',
    'database': '',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# Ініціалізація бота та диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Команда для адміна для редагування тренувань
@dp.message_handler(commands=['editTraining'])
async def edit_training(message: types.Message):
    # Перевірка, чи користувач є адміном
    if str(message.from_user.id) == ADMIN_ID:
        # Створення інлайн-кнопок для редагування днів тижня
        keyboard = InlineKeyboardMarkup(row_width=3)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        buttons = [InlineKeyboardButton(day, callback_data=f"edit_day_{day}") for day in days]
        keyboard.add(*buttons)
        await message.answer("Виберіть день тижня для редагування:", reply_markup=keyboard)
    else:
        await message.answer("Ви не маєте прав для використання цієї команди.")

# Клас для визначення станів користувача при редагуванні тренувань
class EditTrainingStates(StatesGroup):
    edit_day = State()
    edit_time = State()
    edit_theme = State()

# Обробник для редагування дня тренувань
@dp.callback_query_handler(filters.Regexp(r'^edit_day_'))
async def process_edit_day(callback_query: types.CallbackQuery, state: FSMContext):
    await EditTrainingStates.edit_day.set()

    # Отримання дня тижня з callback_data
    day = callback_query.data.split("_")[2]

    # Створення інлайн-кнопок для редагування часу
    keyboard = InlineKeyboardMarkup(row_width=3)
    times = ["7:00 am", "9:00 am", "11:00 am", "2:00 pm"]
    buttons = [InlineKeyboardButton(time, callback_data=f"edit_time_{day}_{time}") for time in times]
    keyboard.add(*buttons)

    await bot.send_message(callback_query.from_user.id, f"Вибрано {day}. Виберіть час тренування:", reply_markup=keyboard)
    await callback_query.answer()

# Обробник для редагування часу тренувань
@dp.callback_query_handler(filters.Regexp(r'^edit_time_'))
async def process_edit_time(callback_query: types.CallbackQuery, state: FSMContext):
    await EditTrainingStates.edit_time.set()

    # Отримання дня тижня та часу з callback_data
    day, time = callback_query.data.split("_")[2], callback_query.data.split("_")[3]

    print(f"Selected day: {day}, time: {time}")

    # Створення інлайн-кнопок для вибору теми тренування
    keyboard = InlineKeyboardMarkup(row_width=3)
    themes = ["Cardio", "Areobic", "Boxing", "Crossfit", "Yoga_Section", "Power lifting", "Body work", "видалити тренерування"]
    buttons = [InlineKeyboardButton(theme, callback_data=f"edit_theme_{day}_{time}_{theme}") for theme in themes]
    keyboard.add(*buttons)

    await bot.send_message(callback_query.from_user.id, f"Вибрано {day} {time}. Виберіть тему тренування:", reply_markup=keyboard)
    await callback_query.answer()

# Обробник для збереження вибору теми тренування
@dp.callback_query_handler(filters.Regexp(r'^edit_theme_'))
async def process_edit_theme(callback_query: types.CallbackQuery, state: FSMContext):
    # Отримання інформації з callback_data
    day, time, theme = callback_query.data.split("_")[2], callback_query.data.split("_")[3], callback_query.data.split("_")[4]

    print(f"Selected day: {day}, time: {time}, theme: {theme}")

    # Підключення до бази даних та виконання SQL-запиту для оновлення інформації про тренування
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            if theme == "видалити тренерування":
                sql = f"UPDATE TrainingSchedule SET {day} = NULL WHERE Time = '{time}'"
            else:
                sql = f"UPDATE TrainingSchedule SET {day} = '{theme}' WHERE Time = '{time}'"
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

    await bot.send_message(callback_query.from_user.id, f"Інформацію оновлено: {day} {time} - {theme}")
    await state.finish()
    await callback_query.answer()

if __name__ == '__main__':
    from aiogram import executor
    from aiogram.contrib.middlewares.logging import LoggingMiddleware

    dp.middleware.setup(LoggingMiddleware())

    executor.start_polling(dp, skip_updates=True)
