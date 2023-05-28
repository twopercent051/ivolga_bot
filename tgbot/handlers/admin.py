from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.filters.state import StateFilter

from create_bot import bot
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import AdminInlineKeyboard as inline_kb
from tgbot.misc.states import AdminFSM
from tgbot.models.redis_connector import RedisConnector as rds
from tgbot.models.sql_connector import TextsDAO

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


@router.message(Command('start'), StateFilter('*'))
async def admin_start_msg(message: Message, state: FSMContext):
    text = 'Здравствуйте. Вы вошли как администратор'
    kb = inline_kb.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'home', StateFilter('*'))
async def admin_start_clb(callback: CallbackQuery, state: FSMContext):
    text = 'Здравствуйте. Вы вошли как администратор'
    kb = inline_kb.main_menu_kb()
    await state.set_state(AdminFSM.home)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == 'edition')
async def text_edition(callback: CallbackQuery):
    button_list = await TextsDAO.get_order_by_parents()
    text = "Выберите что редактируем"
    kb = inline_kb.edition_kb(button_list=button_list, is_main_menu=True)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "add_button")
async def add_button(callback: CallbackQuery):
    button_list = await TextsDAO.get_order_by_parents()
    text = "Выберите дочерний вопрос"
    kb = inline_kb.edition_kb(button_list=button_list, is_main_menu=False)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "parent_id")
async def add_parent(callback: CallbackQuery, state: FSMContext):
    parent_id = int(callback.data.split(":")[1])
    text = "Введите текст на кнопке"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.get_button)
    await state.update_data(parent_id=parent_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.get_button)
async def get_button(message: Message, state: FSMContext):
    value = message.text
    text = "Теперь введите текст после нажатия кнопки"
    kb = inline_kb.home_kb()
    await state.update_data(button_text=value)
    await state.set_state(AdminFSM.get_text)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.get_text)
async def get_text(message: Message, state: FSMContext):
    value = message.html_text
    text = "Вопрос сохранён"
    kb = inline_kb.home_kb()
    state_data = await state.get_data()
    parent_id = state_data["parent_id"]
    button_text = state_data["button_text"]
    await TextsDAO.create(
        parent=parent_id,
        button=button_text,
        text=value
    )
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "edit_button")
async def update_button(callback: CallbackQuery, state: FSMContext):
    button_id = int(callback.data.split(":")[1])
    button = await TextsDAO.get_one_or_none(id=button_id)
    if button["parent"] == 0:
        parent = "Отсутствует"
    else:
        parent_profile = await TextsDAO.get_one_or_none(parent=button["parent"])
        parent = parent_profile["button"]
    text = [
        f"<b>{button['button']}</b>\n",
        f"Родительский вопрос: <i>{parent}</i>",
        f"Текст при нажатии: <i>{button['text']}</i>\n",
        "Что редактируем?"
    ]
    kb = inline_kb.button_or_text()
    await state.update_data(button_id=button_id)
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "edit")
async def update_button(callback: CallbackQuery, state: FSMContext):
    subject = callback.data.split(":")[1]
    text = "Введите новое значение"
    kb = inline_kb.home_kb()
    await state.update_data(subject=subject)
    await state.set_state(AdminFSM.get_subject)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.get_subject)
async def update_button(message: Message, state: FSMContext):
    state_data = await state.get_data()
    button_id = state_data["button_id"]
    text = "Вопрос обновлён"
    kb = inline_kb.home_kb()
    if state_data["subject"] == "button":
        await TextsDAO.update(button_id=button_id, button=message.html_text)
    else:
        await TextsDAO.update(button_id=button_id, text=message.html_text)
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)

