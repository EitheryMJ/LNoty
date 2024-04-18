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

inline_event_buttons = types.InlineKeyboardMarkup()

b1 = types.InlineKeyboardButton(text='Установить оповещение', callback_data='ruoff_set_event')
b2 = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='ruoff_remove_event')

inline_event_buttons.add(b1, b2)


@dp.message_handler(commands=['event'])
async def about_event(message: types.Message):
    await message.answer('Коробка Удачи - временное событие, которое проводится с 6 декабря до 3 января.\n'
                         ' Раз в день на Острове Грёз нужно открывать Сундуки Удачи'
                         ' в 11:30 и 21:30.\n'
                         '\n'
                         'Если повезёт, вы найдёте в сундуке звезду и пройдёте в следующий раунд.'
                         ' А если нет - значит нет.\n'
                         '\n'
                         'В зависимости от количества удачно открытых сундуков вы получите соответствующую награду -'
                         ' тортики и всякая всячина',
                         reply_markup=inline_event_buttons)


@dp.callback_query_handler(filters.Text(contains='ruoff_set_event'))
async def set_event(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
    setting.event = True

    session.commit()

    user.upd_date = datetime.today()
    session.commit()

    session.close()

    await callback_query.message.answer('Оповещение об ивенте установлено')
    await callback_query.answer()


@dp.callback_query_handler(filters.Text(contains='ruoff_remove_event'))
async def remove_event(callback_query: types.CallbackQuery):
    session = Session()

    user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
    setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
    setting.event = False

    session.commit()

    user.upd_date = datetime.today()
    session.commit()

    session.close()

    await callback_query.message.answer('Оповещение об ивенте убрано')
    await callback_query.answer()


async def fantasyisle_notification_wrapper():
    session = Session()
    users = session.query(User).all()
    for user in users:
        setting = session.query(EssenceSetting).filter_by(id_user=user.telegram_id).first()
        if setting.event is True:
            print(user.telegram_id, user.username, 'подходит под оповещение для ивента')
            await fantasyisle_notification(user)
    session.close()


async def fantasyisle_notification(user: User):
    now = datetime.now().strftime('%H:%M')
    try:
        if now == '11:25' or now == '21:25':
            await mybot.send_message(user.telegram_id, '🎂🎂 Коробка Удачи на острове Грёз начинается через 5 минут')
            print(now, user.telegram_id, user.username, 'получил сообщение об ивенте')
        else:
            print(now, 'Неподходящее время для ивента')
    except BotBlocked:
        print('[ERROR] Пользователь заблокировал бота:', now, user.telegram_id, user.username)
