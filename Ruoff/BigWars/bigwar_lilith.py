import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from datetime import datetime
from DataBase.Base import Base
from DataBase.Ruoff import RuoffBigWar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL, TOKEN
from aiogram.utils.exceptions import BotBlocked


mybot = Bot(token=TOKEN)
dp = Dispatcher(mybot)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# LILITH buttons
inline_lilith_buttons = types.InlineKeyboardMarkup()

button_set = types.InlineKeyboardButton(text='Установить оповещение', callback_data='ruoff_set_bigwar_lilith')
button_remove = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='ruoff_remove_bigwar_lilith')

inline_lilith_buttons.add(button_set, button_remove)


# LILITH SETTINGS
@dp.message_handler(commands=['bigwar_lilith'])
async def about_bigwar_lilith(message: types.Message):
    await message.answer('[BIGWAR] Лилит 20:00 [понедельник, четверг] за 15 минут\n',
                         reply_markup=inline_lilith_buttons)


@dp.callback_query_handler(filters.Text(contains='ruoff_set_bigwar_lilith'))
async def set_bigwar_lilith(callback_query: types.CallbackQuery):
    session = Session()

    bg_user = session.query(RuoffBigWar).filter_by(id_user=callback_query.from_user.id).first()
    bg_user.lilith = True
    session.commit()

    session.close()

    await callback_query.message.answer('[BIGWAR] Оповещения о Лилит установлены')
    await callback_query.answer()


@dp.callback_query_handler(filters.Text(contains='ruoff_remove_bigwar_lilith'))
async def remove_bigwar_lilith(callback_query: types.CallbackQuery):
    session = Session()

    bg_user = session.query(RuoffBigWar).filter_by(id_user=callback_query.from_user.id).first()
    bg_user.lilith = False
    session.commit()

    session.close()

    await callback_query.message.answer('[BIGWAR] Оповещения о Лилит убраны')
    await callback_query.answer()


async def bigwar_lilith_notification_wrapper():

    session = Session()
    users = session.query(RuoffBigWar).all()
    for user in users:
        if user.lilith is True:
            await bigwar_lilith_notification(user)
    session.close()


async def bigwar_lilith_notification(user: RuoffBigWar):
    now = datetime.now().strftime('%H:%M')
    try:
        if now == '18:45':
            await mybot.send_message(user.id_user, '🌈🌈 [BIGWAR] Лилит через 15 минут')
            print(now, user.id_user, 'получил сообщение о [BIGWAR] Лилит')

    except BotBlocked:
        print('[ERROR] Пользователь заблокировал бота:', now, user.id_user)
