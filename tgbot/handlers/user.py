import time
from datetime import datetime

import pytz
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from create_bot import bot, config
from tgbot.keyboards.inline import UserInlineKeyboard
from tgbot.misc.states import UserFSM
from tgbot.models.sql_connector import UsersDAO, TextsDAO, WorktimeDAO, TicketsDAO

admin_group = config.tg_bot.admin_group
router = Router()


@router.message(Command('start'))
async def user_start(message: Message):
    text_sql = await TextsDAO.get_one_or_none(type_message="greeting")
    if text_sql:
        text = text_sql["text"]
    else:
        text = "ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ. ВЫ ХОТИТЕ ПОЛУЧАТЬ РАССЫЛКУ?"
    kb = UserInlineKeyboard.mailing_kb()
    rmv_kb = ReplyKeyboardRemove()
    await message.answer("Здравствуйте", reply_markup=rmv_kb)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "mailing")
async def mailing_access(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    name = f"{callback.from_user.first_name} {callback.from_user.last_name}"
    if callback.data.split(":")[1] == "yes":
        mailing = True
    else:
        mailing = False
    try:
        await UsersDAO.create(
            user_id=str(user_id),
            username=str(callback.from_user.username),
            name=str(name),
            mailing=mailing
        )
    except IntegrityError:
        pass
    polling_list = await TextsDAO.get_many(parent=0, type_message="question")
    text_sql = await TextsDAO.get_one_or_none(type_message="choose_question")
    if text_sql:
        text = text_sql["text"]
    else:
        text = "ВЫБЕРИТЕ ИНТЕРЕСУЮЩИЙ ВОПРОС"
    kb = UserInlineKeyboard.parent_polling_kb(polling_list=polling_list)
    await state.set_state(UserFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "question")
@router.callback_query(F.data.split(":")[0] == "back")
async def question_child(callback: CallbackQuery):
    button_id = int(callback.data.split(":")[1])
    polling_list = await TextsDAO.get_many(parent=button_id, type_message="question")
    text_sql = await TextsDAO.get_one_or_none(id=button_id)
    if text_sql:
        parent_id = text_sql["parent"]
        text = text_sql["text"]
        kb = UserInlineKeyboard.child_polling_kb(polling_list=polling_list, parent_id=parent_id)
    else:
        text_sql = await TextsDAO.get_one_or_none(type_message="choose_question")
        if text_sql:
            text = text_sql["text"]
        else:
            text = "ВЫБЕРИТЕ ИНТЕРЕСУЮЩИЙ ВОПРОС"
        kb = UserInlineKeyboard.parent_polling_kb(polling_list=polling_list)
    rmv_kb = ReplyKeyboardRemove()
    await callback.message.answer("Здравствуйте", reply_markup=rmv_kb)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "dialog")
async def dialog(callback: CallbackQuery, state: FSMContext):
    text_sql = await TextsDAO.get_one_or_none(type_message="leave_ticket")
    if text_sql:
        text = text_sql["text"]
    else:
        text = "ОСТАВЬТЕ СВОЁ ОБРАЩЕНИЕ"
    kb = UserInlineKeyboard.home_kb()
    await state.set_state(UserFSM.dialog)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, UserFSM.dialog)
async def dialog(message: Message, state: FSMContext):
    weekday = datetime.now(pytz.timezone('Europe/Moscow')).weekday()
    worktime = await WorktimeDAO.get_one_or_none(day=str(weekday))
    user_id = str(message.from_user.id)
    if worktime:
        now = datetime.now(pytz.timezone('Europe/Moscow')).time()
        if worktime["start"] < now < worktime["finish"]:
            text_sql = await TextsDAO.get_one_or_none(type_message="thank_you")
            if text_sql:
                user_text = text_sql["text"]
            else:
                user_text = "МЫ ПОЛУЧИЛИ ВАШЕ СООБЩЕНИЕ"
        else:
            text_sql = await TextsDAO.get_one_or_none(type_message="rebound")
            if text_sql:
                user_text = text_sql["text"]
            else:
                user_text = "СЕЙЧАС МЫ НЕ РАБОТАЕМ, ОТВЕТИМ ПРИ ПЕРВОЙ ЖЕ ВОЗМОЖНОСТИ"
    else:
        text_sql = await TextsDAO.get_one_or_none(type_message="rebound")
        if text_sql:
            user_text = text_sql["text"]
        else:
            user_text = "СЕЙЧАС МЫ НЕ РАБОТАЕМ, ОТВЕТИМ ПРИ ПЕРВОЙ ЖЕ ВОЗМОЖНОСТИ"
    ticket_hash = f"{user_id}_{int(time.time())}"
    await TicketsDAO.create(user_id=user_id, username=message.from_user.username, text=message.html_text,
                            ticket_hash=ticket_hash)
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    admin_text = f"⚠️ Обращение от клиента {username} \n\n{message.html_text}"
    admin_kb = UserInlineKeyboard.admin_dialog_kb(user_id=user_id, ticket_hash=ticket_hash)
    user_kb = UserInlineKeyboard.home_kb()
    await bot.send_message(chat_id=admin_group, text=admin_text, reply_markup=admin_kb)
    await message.answer(user_text, reply_markup=user_kb)
    await state.set_state(UserFSM.home)
