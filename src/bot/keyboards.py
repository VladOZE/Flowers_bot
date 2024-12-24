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
            InlineKeyboardButton(text='Корзина', callback_data='shopping_cart'),
        ],
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)


SupportMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Связаться с оператором', callback_data='call_operator')
        ],
        [
            InlineKeyboardButton(text='Заполнить форму обратной связи', callback_data='feedback_form')
        ],
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')
        ]
    ]
)


PersonalAccountMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='История заказов', callback_data='orders_history'),
            InlineKeyboardButton(text='Мои адреса', callback_data='my_addresses')
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


BackToMenuFromText = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu_from_text')
        ]
    ]
)


BackToCatalog = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад в каталог', callback_data='back_to_catalog')
        ]
    ]
)


BackToPersonalMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")
        ]
    ]
)


BackToCart = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад в корзину", callback_data="shopping_cart")
        ]
    ]
)


BackToSupportMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад в меню поддержки", callback_data="support")
        ]
    ]
)


BackToAppeals = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад к обращениям", callback_data=f"appeals")
        ]
    ]
)


NewAddressCart = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Новый адрес', callback_data='new_address')
        ],
        [
            InlineKeyboardButton(text='Назад в корзину', callback_data='shopping_cart')
        ]
    ]
)


NewAddressPersonal = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Новый адрес', callback_data='new_address')
        ],
        [
            InlineKeyboardButton(text='Назад в личный кабинет', callback_data='personal_account')
        ]
    ]
)


AddPersonalInfo = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Заполнить данные', callback_data='add_personal_info')
        ],
        [
            InlineKeyboardButton(text='Назад в корзину', callback_data='shopping_cart')
        ]
    ]
)