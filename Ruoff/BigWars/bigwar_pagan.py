import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from datetime import datetime
from DataBase.Base import Base
from DataBase.Ruoff import EssenceBigWar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL, TOKEN
from aiogram.utils.exceptions import BotBlocked


mybot = Bot(token=TOKEN)
dp = Dispatcher(mybot)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# PAGAN buttons
inline_pagan_buttons = types.InlineKeyboardMarkup()

button_set = types.InlineKeyboardButton(text='Установить оповещение', callback_data='ruoff_set_bigwar_pagan')
button_remove = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='ruoff_remove_bigwar_pagan')

inline_pagan_buttons.add(button_set, button_remove)


# PAGAN SETTINGS
@dp.message_handler(commands=['bigwar_pagan'])
async def about_bigwar_pagan(message: types.Message):
    await message.answer('[BIGWAR] Языческий Храм/Крепость Кельбима 22:00 [пятница] за 15 мин\n',
                         reply_markup=inline_pagan_buttons)


@dp.callback_query_handler(filters.Text(contains='ruoff_set_bigwar_pagan'))
async def set_bigwar_pagan(callback_query: types.CallbackQuery):
    session = Session()

    bigwar_user = session.query(EssenceBigWar).filter_by(id_user=callback_query.from_user.id).first()
    bigwar_user.pagan = True
    session.commit()

    session.close()

    await callback_query.message.answer('[BIGWAR] Оповещение о Языческом Храме/Крепость Кельбима установлено')
    await callback_query.answer()


@dp.callback_query_handler(filters.Text(contains='ruoff_remove_bigwar_pagan'))
async def remove_bigwar_pagan(callback_query: types.CallbackQuery):
    session = Session()

    bigwar_user = session.query(EssenceBigWar).filter_by(id_user=callback_query.from_user.id).first()
    bigwar_user.pagan = False
    session.commit()

    session.close()

    await callback_query.message.answer('[BIGWAR] Оповещение о Языческом Храме/Крепость Кельбима убрано')
    await callback_query.answer()


async def bigwar_pagan_notification_wrapper():

    session = Session()
    users = session.query(EssenceBigWar).all()
    for user in users:
        if user.pagan is True:
            await bigwar_pagan_notification(user)
    session.close()


async def bigwar_pagan_notification(user: EssenceBigWar):
    now = datetime.now().strftime('%H:%M')
    try:
        if now == '21:45':
            await mybot.send_message(user.id_user, '🌈🌈 [BIGWAR] Языческий Храм/Крепость Кельбима через 15 минут')
            print(now, '[BIGWAR]', user.id_user, 'получил сообщение о Языческом Храме/Крепость Кельбима')

    except BotBlocked:
        print('[ERROR] Пользователь заблокировал бота:', now, user.id_user)
