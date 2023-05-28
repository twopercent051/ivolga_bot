from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminInlineKeyboard(InlineKeyboardMarkup):
    """Клавиатуры админа"""

    @classmethod
    def home_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def main_menu_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text='Неотвеченные сообщения от клиентов', callback_data='messages')],
            [InlineKeyboardButton(text='Статистика', callback_data='statistics')],
            [InlineKeyboardButton(text='Редактура текстов', callback_data='edition')],
            [InlineKeyboardButton(text='Выгрузка клиентов в CSV', callback_data='download')],
            [InlineKeyboardButton(text='Загрузка клиентов из CSV', callback_data='upload')],
            [InlineKeyboardButton(text='Рассылка', callback_data='mailing')],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def edition_kb(cls, button_list: list, is_main_menu: bool) -> InlineKeyboardMarkup:
        keyboard = []
        action = "edit_button" if is_main_menu else "parent_id"
        for button in button_list:
            clb_text = button["button"] if button["button"] else button["id"]
            keyboard.append([InlineKeyboardButton(text=clb_text, callback_data=f"{action}:{button['id']}")])
        if is_main_menu:
            keyboard.append([InlineKeyboardButton(text="Добавить вопрос", callback_data="add_button")])
            keyboard.append([InlineKeyboardButton(text="Редактура отбойного сообщения", callback_data="edit_rebound")])
        else:
            keyboard.append([InlineKeyboardButton(text="Это родительский вопрос", callback_data="parent_id:0")])
        keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def button_or_text(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text='Текст на кнопке', callback_data='edit:button'),
                InlineKeyboardButton(text='Текст при нажатии', callback_data='edit:text'),
            ],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard
