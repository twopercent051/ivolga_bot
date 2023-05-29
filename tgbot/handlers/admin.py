from datetime import datetime, timedelta

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.utils.markdown import hcode

from create_bot import bot
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import AdminInlineKeyboard as inline_kb
from tgbot.misc.states import AdminFSM
from tgbot.models.sql_connector import TextsDAO, WorktimeDAO, TicketsDAO, UsersDAO

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
        is_rebound=False,
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
        parent_profile = await TextsDAO.get_one_or_none(id=button["parent"])
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


@router.callback_query(F.data.split(":")[0] == "delete_button")
async def delete_button(callback: CallbackQuery, state: FSMContext):
    if callback.data.split(":")[1] == "question":
        text = "Подтвердите удаление вопроса"
        kb = inline_kb.accept_delete_kb()
    else:
        state_data = await state.get_data()
        button_id = state_data["button_id"]
        text = "Вопрос удалён"
        kb = inline_kb.home_kb()
        await TextsDAO.delete(id=button_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "rebound")
async def edit_rebound(callback: CallbackQuery, state: FSMContext):
    chapter = callback.data.split(":")[1]
    if chapter == "start":
        text = "Что редактируем?"
        kb = inline_kb.rebound_menu()
    elif chapter == "text":
        rebound_text_sql = await TextsDAO.get_one_or_none(is_rebound=True)
        rebound_text = rebound_text_sql["text"] if rebound_text_sql else "Текст отсутствует"
        text = f"Сейчас текст отбойного сообщения такой:\n{20 * '*'}\n{rebound_text}\n{20 * '*'}\nВведите новый текст"
        kb = inline_kb.home_kb()
        await state.set_state(AdminFSM.rebound_text)
    else:
        weekdays = {
            0: "Пн",
            1: "Вт",
            2: "Ср",
            3: "Чт",
            4: "Пт",
            5: "Сб",
            6: "Вс",
        }
        text = ["Для редактирования графика скопируйте и отправьте новые значения в таком-же формате через ENTER. "
                "Чтобы сделать день не рабочем поставьте звёздочку (например Пн // *)\n"]
        for day in weekdays.keys():
            worktime_sql = await WorktimeDAO.get_one_or_none(day=str(day))
            if worktime_sql:
                start_time = worktime_sql["start"].strftime("%H:%M")
                finish_time = worktime_sql["finish"].strftime("%H:%M")
                row = hcode(f"{weekdays[day]} // {start_time} - {finish_time}")
            else:
                row = hcode(f"{weekdays[day]} // выходной день")
            text.append(row)
        text = "\n".join(text)
        kb = inline_kb.home_kb()
        await state.set_state(AdminFSM.rebound_worktime)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.rebound_text)
async def edit_rebound_text(message: Message, state: FSMContext):
    text = "Текст отбойного сообщения обновлён"
    kb = inline_kb.home_kb()
    rebound_text = message.html_text
    rebound_text_sql = await TextsDAO.get_one_or_none(is_rebound=True)
    if rebound_text_sql:
        await TextsDAO.update_rebound(text=rebound_text)
    else:
        await TextsDAO.create(text=rebound_text, is_rebound=True)
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.rebound_worktime)
async def edit_rebound_worktime(message: Message, state: FSMContext):
    weekdays = {
        "Пн": 0,
        "Вт": 1,
        "Ср": 2,
        "Чт": 3,
        "Пт": 4,
        "Сб": 5,
        "Вс": 6,
    }
    text = []
    kb = inline_kb.home_kb()
    day_list = message.text.split("\n")
    for day in day_list:
        try:
            weekday = weekdays[day.split("//")[0].strip()]
            if day.split("//")[1].strip() == "*":
                text.append("Новый рабочий график сохранён")
                await WorktimeDAO.delete(day=str(weekday))
            else:
                time_block = day.split("//")[1].strip()
                start_time = datetime.strptime(time_block.split("-")[0].strip(), "%H:%M")
                finish_time = datetime.strptime(time_block.split("-")[1].strip(), "%H:%M")
                if start_time < finish_time:
                    text.append("Новый рабочий график сохранён")
                else:
                    text.append("Время начала не может быть больше времени конца")
                    break
                worktime_sql = await WorktimeDAO.get_one_or_none(day=str(weekday))
                if worktime_sql:
                    await WorktimeDAO.update(day=str(weekday), start=start_time, finish=finish_time)
                else:
                    await WorktimeDAO.create(day=str(weekday), start=start_time, finish=finish_time)
        except IndexError:
            text.append("Неправильный формат")
            break
        except ValueError:
            text.append("Неправильный формат")
            break
    await state.set_state(AdminFSM.home)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.split(":")[0] == "dialog")
async def dialog(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split("|")[0].split(":")[1]
    ticket_hash = callback.data.split("|")[1].split(":")[1]
    text = "Введите текст ответа. Он будет незамедлительно отправлен пользователю, а обращение перейдёт в статус " \
           "завершённых"
    kb = inline_kb.home_kb()
    await state.update_data(user_id=user_id, ticket_hash=ticket_hash)
    await state.set_state(AdminFSM.dialog)
    await callback.message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.dialog)
async def dialog(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data["user_id"]
    ticket_hash = state_data["ticket_hash"]
    admin_text = "Сообщение отправлено"
    admin_kb = inline_kb.home_kb()
    user_text = message.html_text
    await TicketsDAO.update(ticket_hash=ticket_hash, is_finished=True)
    await bot.send_message(chat_id=user_id, text=user_text)
    await message.answer(admin_text, reply_markup=admin_kb)


@router.callback_query(F.data == "tickets")
async def tickets(callback: CallbackQuery):
    ticket_list = await TicketsDAO.get_many(is_finished=False)
    text = "Тут отображаются неотвеченные обращения."
    kb = inline_kb.tickets_kb(ticket_list=ticket_list)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "ticket")
async def tickets(callback: CallbackQuery):
    ticket_id = callback.data.split(":")[1]
    ticket = await TicketsDAO.get_one_or_none(id=ticket_id)
    if ticket:
        ticket_date = (ticket["create_timestamp"] + timedelta(hours=3)).strftime('%d-%m-%Y %H:%M')
        text = [f"Обращение # {ticket_id} от {ticket_date}\n"]
        if ticket["username"]:
            text.append(f'@{ticket["username"]}')
        text.append(ticket["text"])
        kb = inline_kb.ticket_kb(ticket_hash=ticket["ticket_hash"], user_id=ticket["user_id"])
    else:
        text = ["Тикет не найден"]
        kb = inline_kb.home_kb()
    await callback.message.answer("\n".join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "finish_ticket")
async def finish_ticket(callback: CallbackQuery):
    ticket_hash = callback.data.split(":")[1]
    text = "Обращение завершено"
    kb = inline_kb.home_kb()
    await TicketsDAO.update(ticket_hash=ticket_hash, is_finished=True)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.callback_query(F.data.split(":")[0] == "mailing")
async def mailing(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[1]
    if category == "start":
        category_list = await UsersDAO.get_categories()
        text = "Выберите категорию для рассылки"
        kb = inline_kb.categories_kb(category_list=category_list)
    else:
        text = "Введите сообщение. Оно будет отправлено всем пользователям"
        kb = inline_kb.home_kb()
        await state.update_data(category=category)
        await state.set_state(AdminFSM.mailing)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.mailing)
async def mailing(message: Message, state: FSMContext):
    state_data = await state.get_data()
    category = state_data["category"]
    if category == "all":
        user_list = await UsersDAO.get_many(mailing=True)
    else:
        user_list = await UsersDAO.get_many(mailing=True, category=category)
    counter = 0
    for user in user_list:
        user_id = user["user_id"]
        try:
            await bot.send_message(chat_id=user_id, text=message.html_text)
            counter += 1
        except TelegramBadRequest:
            pass
    admin_text = f"Разослали {counter} из {len(user_list)} пользователей"
    kb = inline_kb.home_kb()
    await state.set_state(AdminFSM.home)
    await message.answer(admin_text, reply_markup=kb)
