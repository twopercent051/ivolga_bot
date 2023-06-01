from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    get_button = State()
    get_text = State()
    get_subject = State()
    edit_message = State()
    rebound_worktime = State()
    dialog = State()
    mailing = State()
    upload = State()


class UserFSM(StatesGroup):
    home = State()
    dialog = State()
