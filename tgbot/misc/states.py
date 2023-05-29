from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_button = State()
    get_text = State()
    get_subject = State()
    rebound_text = State()
    rebound_worktime = State()
    dialog = State()
    mailing = State()


class UserFSM(StatesGroup):
    home = State()
    dialog = State()
