import asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
from DataBase.User import User
from DataBase.Base import Base
from DataBase.Ruoff import LegacySetting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL, TOKEN, test_token
from aiogram.utils.exceptions import BotBlocked
from Commands.options import options_menu_text
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU')


mybot = Bot(token=TOKEN)
dp = Dispatcher(mybot, storage=MemoryStorage())

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


class LegacyGardensTime(StatesGroup):
    waiting_for_legacy_gardens_time = State()


# gardens buttons
inline_legacy_gardens_buttons = types.InlineKeyboardMarkup()

button_set = types.InlineKeyboardButton(text='Установить оповещение', callback_data='ruoff_option_set_legacy_gardens')
button_set_time = types.InlineKeyboardButton(text='Установить время', callback_data='ruoff_option_set_legacy_time_gardens')
button_remove = types.InlineKeyboardButton(text='Убрать оповещение', callback_data='ruoff_option_remove_legacy_gardens')

button_back = types.InlineKeyboardButton(text='<< резко передумать и вернуться',
                                         callback_data='ruoff_option_cancel_to_set_legacy_gardens')
button_menu = types.InlineKeyboardButton(text='Вернуться к списку активностей',
                                         callback_data='ruoff_option_cancel_to_set_legacy_gardens')

inline_legacy_gardens_buttons.add(button_set, button_remove)


# LEGACY GARDENS SETTINGS
@dp.message_handler(commands=['legacy_gardens'])
async def about_legacy_gardens(message: types.Message):
    try:
        with Session() as session:

            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            option_setting = session.query(LegacySetting).filter_by(id_user=user.telegram_id).first()
            if not option_setting:
                option = LegacySetting(id_user=user.telegram_id)
                session.add(option)
                session.commit()

        text = 'Забытый Первобытный Сад — особая зона охоты для персонажей от 76 уровня и выше.\n'\
               'В зоне дается бесплатно 7 часов в неделю, присутствуют еженедельные задания, \n'\
               'В разные дни можно выбить разные талисманы с монстров.\n'\
               '\n'\
               'В 22:00 появляется РБ Кадин\n'\               

        await mybot.send_message(chat_id=message.from_user.id,
                                 text=text,
                                 reply_markup=inline_legacy_gardens_buttons)

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[LEGACY GARDENS] {message.from_user.id} - Произошла ошибка в функции about_legacy_gardens: {e}')


# SELECT MENU FOR LEGACY GARDENS TIME
@dp.callback_query_handler(filters.Text(contains='ruoff_option_set_legacy_gardens'))
async def set_legacy_gardens(callback_query: types.CallbackQuery):
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=2).add(button_set_time, button_back)
        await mybot.edit_message_text(chat_id=callback_query.from_user.id,
                                      message_id=callback_query.message.message_id,
                                      text='Сейчас вы в меню настроек оповещений [Legacy] Забытого Сада 🧐',
                                      reply_markup=keyboard)
        await callback_query.answer()

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[LEGACY GARDENS] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции set_legacy_gardens: {e}')


# CANCEL MENU LEGACY GARDENS TIME
@dp.callback_query_handler(filters.Text(contains='ruoff_option_cancel_to_set_legacy_gardens'))
async def cancel_to_set_legacy_gardens(callback_query: types.CallbackQuery):
    try:
        await mybot.answer_callback_query(callback_query.id)
        await mybot.edit_message_text(chat_id=callback_query.from_user.id,
                                      message_id=callback_query.message.message_id,
                                      text=options_menu_text)

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[LEGACY GARDENS] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции cancel_to_set_legacy_gardens: {e}')


# INPUT LEGACY GARDENS TIME
@dp.callback_query_handler(filters.Text(contains='ruoff_option_set_legacy_time_gardens'))
async def set_legacy_gardens_time(callback_query: types.CallbackQuery):
    try:
        keyboard = types.InlineKeyboardMarkup().add(button_back)
        text = f'НАПИШИТЕ время оповещения для [Legacy] Забытых Садов в формате час:минута (например, 10:21 или 01:24): '
        await mybot.edit_message_text(chat_id=callback_query.from_user.id,
                                      message_id=callback_query.message.message_id,
                                      text=text,
                                      reply_markup=keyboard)

        await LegacyGardensTime.waiting_for_legacy_gardens_time.set()
        await callback_query.answer()

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[Legacy GARDENS] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции set_legacy_gardens_time: {e}')


# SAVE LEGACY GARDENS TIME
@dp.message_handler(state=LegacyGardensTime.waiting_for_legacy_gardens_time)
async def save_legacy_gardens_time(message: types.Message, state: FSMContext):
    try:
        gardens = message.text
        hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                 '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
        minutes = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
        for h in range(10, 61):
            minutes.append(str(h))

        if len(gardens) == 5 and gardens[:2] in hours and gardens[2] == ':' and gardens[3:5] in minutes:
            with Session() as session:

                user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
                option_setting = session.query(LegacySetting).filter_by(id_user=user.telegram_id).first()
                option_setting.gardens = gardens
                session.commit()
    
                user.upd_date = datetime.today()
                session.commit()

            keyboard = types.InlineKeyboardMarkup(row_width=2).add(button_menu)

            await mybot.send_message(chat_id=message.from_user.id,
                                     text=f'Вы установили время для оповещений [Legacy] Забытых Садов - {gardens}',
                                     reply_markup=keyboard)

        else:
            await mybot.send_message(chat_id=message.from_user.id,
                                     text='Неправильный формат времени, пожалуйста, попробуйте еще раз.')
            return

        await state.finish()

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[Legacy GARDENS] {message.from_user.id} - '
                                      f'Произошла ошибка в функции save_legacy_gardens_time: {e}')


# CANCEL SET LEGACY GARDENS TIME
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ruoff_option_cancel_to_set_legacy_gardens',
                           state=LegacyGardensTime.waiting_for_legacy_gardens_time)
async def cancel_to_set_legacy_gardens_time(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await mybot.answer_callback_query(callback_query.id)
        await mybot.edit_message_text(chat_id=callback_query.from_user.id,
                                      message_id=callback_query.message.message_id,
                                      text=options_menu_text)
        await state.finish()

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[Legacy GARDENS] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции cancel_to_set_legacy_gardens_time: {e}')


# REMOVE LEGACY GARDENS TIME
@dp.callback_query_handler(filters.Text(contains='ruoff_option_remove_legacy_gardens'))
async def remove_legacy_gardens(callback_query: types.CallbackQuery):
    try:
        with Session() as session:

            user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
            option_setting = session.query(LegacySetting).filter_by(id_user=user.telegram_id).first()
            option_setting.gardens = None
    
            session.commit()

        keyboard = types.InlineKeyboardMarkup(row_width=2).add(button_menu)

        await mybot.edit_message_text(chat_id=callback_query.from_user.id,
                                      message_id=callback_query.message.message_id,
                                      text='Оповещение о [Legacy] Забытых Садах убрано',
                                      reply_markup=keyboard)
        await callback_query.answer()

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[Legacy GARDENS] {message.from_user.id} - '
                                      f'Произошла ошибка в функции remove_legacy_gardens: {e}')


# SELECT USER WITH TRUE SETTING
async def legacy_gardens_notification_wrapper():
    try:
        with Session() as session:
            users = session.query(User).all()
    
            for user in users:
                option = session.query(LegacySetting).filter_by(id_user=user.telegram_id).first()
                if option and option.gardens:
                    await legacy_gardens_notification(user)

    except Exception as e:
        await mybot.send_message(chat_id='952604184',
                                 text=f'[Legacy GARDENS] {message.from_user.id} - '
                                      f'Произошла ошибка в функции legacy_gardens_notification_wrapper: {e}')


# SEND GARDENS MESSAGE
async def legacy_gardens_notification(user: User):
    try:
        now = datetime.now().strftime('%H:%M')

        with Session() as session:
            option = session.query(LegacySetting).filter_by(id_user=user.telegram_id).first()

        gardens = option.gardens if option.gardens else None
        # если не время и не место
        if gardens and now != gardens:
            return      

        # финальная напоминалка       
        elif gardens and now == gardens and datetime.today().strftime('%A').lower() == 'вторник':
            try:
                await mybot.send_message(
                    user.telegram_id,
                    'Завтра Забытые Сады обновятся, ничего не забыл сделать?'
                )
                print(now, user.telegram_id, user.username, 'получил сообщение о Забытых Садах')
            except BotBlocked:
                print('[ERROR] Пользователь заблокировал бота:', now, user.telegram_id, user.username)
                
         # ежедневная напоминалка
        elif gardens and now == gardens:
            try:
                await mybot.send_message(
                    user.telegram_id,
                    'Пора посетить Забытый Первобытный Сад и что-то там поделать'
                )
                print(now, user.telegram_id, user.username, 'получил сообщение о [Legacy] Забытых Садах')
            except BotBlocked:
                print('[ERROR] Пользователь заблокировал бота:', now, user.telegram_id, user.username)

    except Exception as e:
        await mybot.send_message(
            chat_id='952604184',
            text=f'[Legacy GARDENS] {message.from_user.id} - Произошла ошибка в функции legacy_gardens_notification: {e}'
        )
