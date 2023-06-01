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
            [InlineKeyboardButton(text='Неотвеченные сообщения от клиентов', callback_data='tickets')],
            [InlineKeyboardButton(text='Статистика', callback_data='statistics')],
            [InlineKeyboardButton(text='Редактура текстов', callback_data='edition')],
            [InlineKeyboardButton(text='Выгрузка клиентов в XLSX', callback_data='download')],
            [InlineKeyboardButton(text='Загрузка клиентов из XLSX', callback_data='upload')],
            [InlineKeyboardButton(text='Рассылка', callback_data='mailing:start')],
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
            keyboard.append([InlineKeyboardButton(text="➕ Добавить вопрос", callback_data="add_button")])
            keyboard.append([InlineKeyboardButton(text="🙋 Приветствие", callback_data="type_msg:greeting")])
            keyboard.append([InlineKeyboardButton(text="❔ Выберите вопрос", callback_data="type_msg:choose_question")])
            keyboard.append([InlineKeyboardButton(text="📄 Оставьте обращение", callback_data="type_msg:leave_ticket")])
            keyboard.append([InlineKeyboardButton(text="🛠 Мы работаем", callback_data="type_msg:thank_you")])
            keyboard.append([InlineKeyboardButton(text="🛏 Мы не работаем", callback_data="rebound:start")])
        else:
            keyboard.append([InlineKeyboardButton(text="👨‍👦‍👦 Это родительский вопрос", callback_data="parent_id:0")])
        keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def button_or_text(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text='Текст на кнопке', callback_data='edit:button'),
                InlineKeyboardButton(text='Текст при нажатии', callback_data='edit:text'),
                InlineKeyboardButton(text='Удалить вопрос', callback_data='delete_button:question'),
            ],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def accept_delete_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Подтверждаю", callback_data="delete_button:accept"),
                InlineKeyboardButton(text="🏠 Главное меню", callback_data="home"),
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def rebound_menu(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text='Текст', callback_data='rebound:text'),
                InlineKeyboardButton(text='Рабочее время', callback_data='rebound:worktime'),
            ],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def tickets_kb(cls, ticket_list: list) -> InlineKeyboardMarkup:
        keyboard = []
        for ticket in ticket_list:
            keyboard.append([InlineKeyboardButton(text=f"Обращение # {ticket['id']}",
                                                  callback_data=f"ticket:{ticket['id']}")])
        keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def ticket_kb(cls, ticket_hash, user_id) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="↩️ Ответить", callback_data=f"dialog:{user_id}|ticket:{ticket_hash}")],
            [InlineKeyboardButton(text="Завершить без ответа", callback_data=f"finish_ticket:{ticket_hash}")],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def categories_kb(cls, category_list: list | None) -> InlineKeyboardMarkup:
        keyboard = []
        for category in category_list:
            if category["category"]:
                keyboard.append([InlineKeyboardButton(text=category["category"],
                                                      callback_data=f"mailing:{category['category']}")])
        keyboard.append([InlineKeyboardButton(text="Все пользователи", callback_data=f"mailing:all")])
        keyboard.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def url_mailing_kb(cls, text: str, url: str) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text=text, url=url)],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def mailing_accept_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Подтверждаю", callback_data="mailing:accept"),
                InlineKeyboardButton(text="Нет, надо исправить", callback_data="mailing:start"),
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard


class UserInlineKeyboard(InlineKeyboardMarkup):
    """Клавиатуры пользователя"""

    @classmethod
    def mailing_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text='Да', callback_data='mailing:yes'),
                InlineKeyboardButton(text='Нет', callback_data='mailing:no'),
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def parent_polling_kb(cls, polling_list: list) -> InlineKeyboardMarkup:
        keyboard = []
        for button in polling_list:
            keyboard.append([InlineKeyboardButton(text=button["button"], callback_data=f"question:{button['id']}")])
        keyboard.append([InlineKeyboardButton(text="Связаться с администратором", callback_data="dialog:start")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def child_polling_kb(cls, polling_list: list, parent_id: int) -> InlineKeyboardMarkup:
        keyboard = []
        for button in polling_list:
            keyboard.append([InlineKeyboardButton(text=button["button"], callback_data=f"question:{button['id']}")])
        keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"back:{parent_id}")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def home_kb(cls) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back:0")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def admin_dialog_kb(cls, user_id: str, ticket_hash: str) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="↩️ Ответить", callback_data=f"dialog:{user_id}|ticket:{ticket_hash}")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard
