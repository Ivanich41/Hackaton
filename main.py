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
import time

conn = sqlite3.connect('database.db')
c = conn.cursor()
#c.execute("DROP TABLE tasks")
c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title TEXT, message_id TEXT, solved_by TEXT, dead_line TEXT)''')
conn.commit()

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
    setting_deadline = State()
    choosing_task = State()


@dp.message_handler(commands=['start'])
async def get_keyboard(message: types.Message):
    teacher = False
    if teacher:
        await Form.idle.set()
        await message.answer('Меню', reply_markup=teacher_main_kb)
        c.execute(f'''INSERT OR IGNORE INTO users VALUES ("{message.from_user.id}", TRUE, NULL)
                  ''')
    else:
        await Form.idle.set()
        await message.answer('Меню', reply_markup=students_main_kb)
        c.execute(f'''INSERT OR IGNORE INTO users VALUES ("{message.from_user.id}", FALSE, NULL)
                  ''')
    conn.commit()


# ==============================TEACHERS BEGIN==============================
@dp.message_handler(lambda message: 'Добавить задание' in message.text, state=Form.idle)
async def add_task(message: types.Message):
    await message.answer('Отправьте фотографии', reply_markup=teacher_main_kb)
    await Form.creating_task.set()


@dp.message_handler(state=Form.creating_task)
async def create_task(message: types.Message, state: FSMContext):
    msg_id = message.message_id
    await Form.setting_deadline.set()
    deadline_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    deadline_kb.add(KeyboardButton('1 день'))
    deadline_kb.add(KeyboardButton('1 час'))
    deadline_kb.add(KeyboardButton('30 минут'))
    await message.answer('Выберите время на выполнение или укажите свое время в часах', reply_markup=deadline_kb)
    async with state.proxy() as data:
        data['msg_id'] = msg_id
        data['title'] = message.text.split("\n")[0]

@dp.message_handler(state=Form.setting_deadline)
async def create_task2(message: types.Message, state: FSMContext):
    deadline = 0
    async with state.proxy() as data:
        msg_id = data['msg_id'] 
        txt = message.text
        if 'час' in message.text:
            deadline = int(txt.split()[0]) * 60 * 60
        elif 'день' in message.text:
            deadline =  int(txt.split()[0]) * 60 * 60 * 24
        elif 'минут' in message.text:
            deadline =  int(txt.split()[0]) * 60
        else:
            deadline =  int(txt.split()[0]) * 60 * 60
        print(msg_id)   
        await bot.send_message(message.from_user.id, 'Задание отправлено ученикам', reply_markup=teacher_main_kb)
        await Form.idle.set()
        #sending new task to students
        users = c.execute("""SELECT user_id FROM users WHERE is_teacher == FALSE""")
        records = c.fetchall()
        print(time.time(), deadline)
        title = data['title']
        c.execute(f"""INSERT INTO tasks (title, message_id, solved_by, dead_line) VALUES ('{title}', '{msg_id}', '', '{int(time.time()) + deadline}')""")
        for user in records:
            await bot.forward_message(int(user[0]), message.from_user.id, msg_id)
            deadline_msg = f"Дедлайн до: {time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time() + deadline)))} \nЧасов осталось: {deadline / 60 / 60}"
            await bot.send_message(int(user[0]), deadline_msg, reply_markup=teacher_main_kb)
            conn.commit()
    await Form.idle.set()


    # forward to everyone
    await Form.idle.set()

def create_task(title, text, photo):
    pass
    # may be title text not needed

# ==============================TEACHERS END==============================



# ==============================STUDENTS==============================

# в отображении кнопок будут проблемы т.к есть ограничение на их количество
#students_main_kb
@dp.message_handler(lambda message: message.text == 'Список заданий', state=Form.idle)
async def get_tasks(message: types.Message):
    # get messages ids from db
    sers = c.execute("""SELECT *  FROM tasks""")
    records = c.fetchall()
    print(records)
    tasks = [x for x in records if str(message.from_user.id) not in x[3]]
    ans = ""
    tasks_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for task in tasks:
        timeleft = int(task[4]) - int(time.time())
        if timeleft > 0:
            tasks_kb.add(KeyboardButton(f"{task[1]} - Осталось {timeleft}"))    
        else:
            tasks_kb.add(KeyboardButton(f"{task[1]} - Просрочено"))    

    tasks_kb.add(KeyboardButton(f"Вернуться в меню"))    

    await message.answer(f'Список ваших заданий: {tasks}', reply_markup=tasks_kb)
    await Form.choosing_task.set()


@dp.message_handler(lambda message: 'Вернуться в меню' in message.text, state=Form.choosing_task)
async def get_tasks(message: types.Message):
    await get_keyboard(message)

# ==============================STUDENTS END==============================


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
