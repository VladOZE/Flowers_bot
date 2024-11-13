from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


StartMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Каталог', callback_data='catalog'),
            InlineKeyboardButton(text='Примеры работ', callback_data='examples')
        ],
        [
            InlineKeyboardButton(text='Поддержка', callback_data='support'),
            InlineKeyboardButton(text='О нас', callback_data='about')
        ],
        [
            InlineKeyboardButton(text='Личный кабинет', callback_data='personal_account'),
        ]
    ]
)


CatalogMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Цветы', callback_data='flowers'),
            InlineKeyboardButton(text='Букеты', callback_data='bouquets')
        ],
        [
            InlineKeyboardButton(text='Игрушки', callback_data='toys'),
            InlineKeyboardButton(text='Персональный заказ', callback_data='personal_order')
        ],
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)


SupportMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Связаться с оператором', callback_data='flowers')
        ],
        [
            InlineKeyboardButton(text='Заполнить форму обратной связи', callback_data='bouquets')
        ],
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)


PersonalAccountMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='История заказов', callback_data='orders'),
            InlineKeyboardButton(text='Мои адреса', callback_data='addresses')
        ],
        [
            InlineKeyboardButton(text='Мои обращения в поддержку', callback_data='appeals'),
            InlineKeyboardButton(text='Настройки рассылки', callback_data='mailing')
        ],
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)


BackToMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)