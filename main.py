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
#c.execute("DROP TABLE users")
c.execute('''
          CREATE TABLE IF NOT EXISTS users
          (user_id TEXT PRIMARY KEY, is_teacher BOOLEAN DEFAULT FALSE, teacher DEFAULT NULL)
          ''')
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
    chosen_task = State()
    sending_task = State()

@dp.message_handler(commands=['start'])
async def get_keyboard(message: types.Message):
    await Form.idle.set()
    await message.answer('Меню', reply_markup=teacher_main_kb)
    c.execute(f'''INSERT OR IGNORE INTO users VALUES ("{message.from_user.id}", TRUE, NULL)
              ''')
    conn.commit()

@dp.message_handler(commands=['start2'])
async def get_keyboard(message: types.Message):
    await Form.idle.set()
    await message.answer('Меню', reply_markup=students_main_kb)
    c.execute(f'''INSERT OR IGNORE INTO users VALUES ("{message.from_user.id}", FALSE, 408512172)
              ''')
    conn.commit()

# ==============================TEACHERS BEGIN==============================
@dp.message_handler(lambda message: 'Добавить задание' in message.text, state=Form.idle)
async def add_task(message: types.Message):
    await message.answer('Отправьте новое задание', reply_markup=teacher_main_kb)
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
        print(records)
        title = data['title']
        c.execute(f"""INSERT INTO tasks (title, message_id, solved_by, dead_line) VALUES ('{title}', '{msg_id}', '', '{int(time.time()) + deadline}')""")
        for user in records:
            await bot.forward_message(int(user[0]), message.from_user.id, msg_id)
            deadline_msg = f"Дедлайн до: {time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time() + deadline)))} \nЧасов осталось: {deadline / 60 / 60}"
            await bot.send_message(int(user[0]), deadline_msg)
            conn.commit()
    await Form.idle.set()

# ==============================TEACHERS END==============================



# ==============================STUDENTS==============================

# в отображении кнопок будут проблемы т.к есть ограничение на их количество
#students_main_kb
@dp.message_handler(lambda message: 'Список заданий' in message.text, state=Form.idle)
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

    tasks_kb.add(KeyboardButton(f"Назад"))    

    await message.answer(f'Список ваших заданий: {tasks}', reply_markup=tasks_kb)
    await Form.chosen_task.set()


@dp.message_handler(lambda message: 'Назад' not in message.text, state=Form.chosen_task)
async def chosen_task(message: types.Message, state: FSMContext):
    title = message.text.split(' - ')[0]
    chosen_task = ReplyKeyboardMarkup(resize_keyboard=True)  
    chosen_task.add(KeyboardButton(f"Назад"))
    users = c.execute(f"""SELECT teacher FROM users WHERE user_id == {message.from_user.id}""")
    records = c.fetchall()
    teacher = int(records[0][0])
    tasks = c.execute(f"""SELECT message_id, dead_line FROM tasks WHERE title == '{title}'""")
    records2 = c.fetchall()
    message_id = int(records2[0][0])
    islate = False if int(records2[0][1]) > int(time.time()) else True
    async with state.proxy() as data:
        data['teacher'] = teacher
        data['title'] = title
        data['islate'] = islate
    await bot.forward_message(message.from_user.id, teacher, int(message_id))
    await bot.send_message(message.from_user.id, 'Отправьте решение или вернитесь к списку заданий', reply_markup=chosen_task)
    await Form.sending_task.set()

@dp.message_handler(content_types=['photo', 'text'], state=Form.sending_task)
async def sending_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        teacher = data['teacher'] 
        title = data['title']
        islate = data['islate']
        users = c.execute(f"""UPDATE tasks SET solved_by = (solved_by || '{message.from_user.id} ') WHERE title == '{title}'""")
        conn.commit()
        await bot.send_message(teacher, f'Новое решение от {message.from_user.first_name} {message.from_user.last_name} {"с опозданием!" if islate else ""}')
        await bot.forward_message(teacher, message.from_user.id, message.message_id)
        await bot.send_message(message.from_user.id, 'Решение отправлено учителю', reply_markup=students_main_kb)
        await Form.idle.set()
    

@dp.message_handler(lambda message: 'Назад' in message.text, state=Form.sending_task)
async def back_to_menu(message: types.Message):
    Form.idle.set()
    await get_tasks(message)
@dp.message_handler(lambda message: 'Назад' in message.text, state=Form.chosen_task)
async def back_to_menu(message: types.Message):
    await Form.idle.set()
    await get_keyboard(message)



@dp.message_handler()
async def log_message(message: types.Message):
    print(message)
# ==============================STUDENTS END==============================
    

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
