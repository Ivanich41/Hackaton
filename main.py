import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import sqlite3
con = sqlite3.connect('database.db')
cur = con.cursor()

API_TOKEN = '5595903898:AAGe4opPP1_Yuxe5Tw8TsT07FGe56mgj1i4'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Keyboards
teacher_main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
teacher_main_kb.add(KeyboardButton('Добавить задание'))

students_main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
students_main_kb.add(KeyboardButton('Список заданий'))


class Form(StatesGroup):
    idle = State()
    creating_task = State()


@dp.message_handler(commands=['start'])
async def getkeyboard(message: types.Message):
    teacher = False
    if teacher:
        await Form.idle.set()
        await message.answer('Бот запущен', reply_markup=teacher_main_kb)
    else:
        await message.answer('Бот запущен', reply_markup=students_main_kb)


# ==============================TEACHERS BEGIN==============================
@dp.message_handler(lambda message: message.text == 'Добавить задание')
async def add_task(message: types.Message):
    await message.answer('Отправьте фотографии', reply_markup=teacher_main_kb)
    await Form.creating_task.set()

@dp.message_handler(state=Form.creating_task)
async def create_task(message: types.Message):

    title = message.text.split("\n")[0]
    text = message.text.split("\n")[1:]
    Form.creating_task.set()
    await bot.send_message(message.from_user.id, 'Задание отправлено ученикам', reply_markup=teacher_main_kb)
    await Form.idle.set()
    #sending new task to students
    await bot.forward_message(message.from_user.id, message.from_user.id, message.message_id) 
    # forward to everyone



def create_task(title, text, photo):
    pass
    # may be title text not needed

# ==============================TEACHERS END==============================



# ==============================STUDENTS==============================

# в отображении кнопок будут проблемы т.к есть ограничение на их количество
#students_main_kb
@dp.message_handler(lambda message: message.text == 'Список заданий')
async def get_tasks(message: types.Message):
    tasks = get_all_tasks()
    await message.answer('Список ваших заданий: {}', reply_markup=students_main_kb)
    await Form.idle.set()


def get_all_tasks():
    # get messages ids from db
    return 0

# ==============================STUDENTS END==============================


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
