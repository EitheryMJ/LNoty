import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from datetime import datetime
from DataBase.User import User
from DataBase.Base import Base
from DataBase.Expanse import Expanse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL, TOKEN

mybot = Bot(token=TOKEN)
dp = Dispatcher(mybot)

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

# hellbound buttons
inline_hellbound_buttons = types.InlineKeyboardMarkup()

b16 = types.InlineKeyboardButton(text='Установить оповещение', callback_data='expanse_sethellbound')
b17 = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='expanse_removehellbound')

inline_hellbound_buttons.add(b16, b17)


# HELLBOUND SETTINGS
@dp.message_handler(commands=['expanse_hellbound'])
async def expanse_about_hellbound(message: types.Message):
    await message.answer('Остров Ада — межсерверная зона охоты для персонажей 85+ и'
                         ' доступна в субботу с 10:00 до 00:00.',
                         reply_markup=inline_hellbound_buttons)


@dp.callback_query_handler(filters.Text(contains='expanse_sethellbound'))
async def expanse_set_hellbound(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(Expanse).filter_by(id_user=user.telegram_id).first()
    setting.hellbound = True

    session.commit()
    session.close()

    await callback_query.message.answer('Оповещение об открытии и закрытии Острова Ада установлено')
    await callback_query.answer()


@dp.callback_query_handler(filters.Text(contains='expanse_removehellbound'))
async def expanse_remove_hellbound(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(Expanse).filter_by(id_user=user.telegram_id).first()
    setting.hellbound = False

    session.commit()
    session.close()

    await callback_query.message.answer('Оповещение об открытии и закрытии Острова Ада убрано')
    await callback_query.answer()


async def expanse_hellbound_notification_wrapper():
    session = Session()
    users = session.query(User).all()

    for user in users:
        setting = session.query(Expanse).filter_by(id_user=user.telegram_id).first()
        if setting.hellbound is True:
            await expanse_hellbound_notification(user)
    session.close()


async def expanse_hellbound_notification(user: User):
    now = datetime.now().strftime('%H:%M')
    if now == '09:55':
        await mybot.send_message(user.telegram_id, '🔥 Остров Ада откроется через 5 минут')
        print(now, user.telegram_id, user.username, 'получил сообщение об открытии Острова Ада')
    elif now == '17:55':
        await mybot.send_message(user.telegram_id, '🔥 Цитадель на Острове Ада откроется через 5 минут')
        print(now, user.telegram_id, user.username, 'получил сообщение об открытии Цитадели Острова Ада')
    elif now == '22:59':
        await mybot.send_message(user.telegram_id, '🔥 До закрытия Острова Ада остался часик')
        print(now, user.telegram_id, user.username, 'получил сообщение о закрытии Острова Ада')
    else:
        print(now, 'Неподходящее время для Острова Ада')
