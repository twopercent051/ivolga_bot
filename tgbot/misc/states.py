from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_button = State()
    get_text = State()
    get_subject = State()