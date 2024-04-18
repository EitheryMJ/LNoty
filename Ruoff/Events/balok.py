import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from datetime import datetime
from DataBase.User import User
from DataBase.Base import Base
from DataBase.Ruoff import EssenceSetting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL, TOKEN
from aiogram.utils.exceptions import BotBlocked


mybot = Bot(token=TOKEN)
dp = Dispatcher(mybot)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# balok buttons
inline_balok_buttons = types.InlineKeyboardMarkup()

b12 = types.InlineKeyboardButton(text='Установить оповещение', callback_data='ruoff_setbalok')
b13 = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='ruoff_removebalok')

inline_balok_buttons.add(b12, b13)


@dp.message_handler(commands=['balok'])
async def about_balok(message: types.Message):
    await message.answer('Битва с Валлоком проводится ежедневно, кроме воскресенья в 20:30',
                         reply_markup=inline_balok_buttons)


@dp.callback_query_handler(filters.Text(contains='ruoff_setbalok'))
async def set_balok(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
    setting.balok = True

    session.commit()

    user.upd_date = datetime.today()
    session.commit()

    session.close()

    await callback_query.message.answer('Оповещение о начале Битвы с Валлоком установлено')
    await callback_query.answer()


@dp.callback_query_handler(filters.Text(contains='ruoff_removebalok'))
async def remove_balok(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
    setting.balok = False

    session.commit()

    user.upd_date = datetime.today()
    session.commit()

    session.close()

    await callback_query.message.answer('Оповещение о начале Битвы с Валлоком убрано')
    await callback_query.answer()


async def balok_notification_wrapper():

    session = Session()
    users = session.query(User).all()

    for user in users:
        setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
        if setting.balok is True:
            await balok_notification(user)
    session.close()


async def balok_notification(user: User):
    now = datetime.now().strftime('%H:%M')
    try:
        if now == '20:25':
            await mybot.send_message(user.telegram_id, '🗡️🗡️ Битва с Валлоком начнется через 5 минут')
            print(now, user.telegram_id, user.username, 'получил сообщение о Битве с Валлоком')
        else:
            print(now, 'Неподходящее время для Битвы с Валлоком')
    except BotBlocked:
        print('[ERROR] Пользователь заблокировал бота:', now, user.telegram_id, user.username)
