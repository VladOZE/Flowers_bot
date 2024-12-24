from typing import Tuple, List
from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, BotCommandScopeDefault
from src.database.models import *
import os
from keyboards import BackToPersonalMenu


# Отсюда начинается блок кода с функциями для класса MainMenuCallback
def main_menu_text() -> Tuple[str, str]:
    menu_text = 'Добро пожаловать в цветочный магазин FlowersMarket'
    menu_photo_path = "../images/menu/main_menu.jpeg"

    return menu_text, menu_photo_path


def catalog_menu_text() -> Tuple[str, str]:
    catalog_text = 'Пожалуйста, выберите категорию товаров из предложенных ниже'
    catalog_photo_path = "../images/menu/catalog_menu.jpg"

    return catalog_text, catalog_photo_path


def support_menu_text() -> Tuple[str, str]:
    support_text = (
        "Добро пожаловать в раздел технической поддержки магазина <b>Flowers Market</b>!\n\n"
        "Вы можете связаться с оператором, нажав на соответствующую кнопку снизу, "
        "или заполнить форму обратной связи, и мы свяжемся с вами как можно скорее!"
    )
    support_photo_path = "../images/menu/support_menu.jpg"

    return support_text, support_photo_path


def about_menu_text() -> Tuple[str, str]:
    about_text = (
        "<b>О нас</b>\n\n"
        "     Мы — команда флористов, объединённых страстью к "
        "<b>искусству цветочного дизайна</b> и стремлением создавать "
        "уникальные и запоминающиеся букеты.\n\n"
        "     <b>Наша работа</b> — это не просто создание букетов, а настоящая "
        "магия, превращающая каждый цветок в произведение искусства.\n\n"
        "     Мы верим, что каждый элемент природы способен рассказать "
        "свою историю и вызвать особые эмоции."
    )
    about_photo_path = "../images/menu/about_menu.jpg"

    return about_text, about_photo_path


def personal_account_menu_text() -> Tuple[str, str]:
    personal_account_text = ("Добро пожаловать в личный кабинет пользователя!")
    personal_account_photo_path = "../images/menu/personal_account_menu.jpg"

    return personal_account_text, personal_account_photo_path


def create_examples_gallery() -> List[str]:
    path = "../images/examples/"
    gallery = sorted(
        [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))])
    return gallery


def create_keyboard_for_gallery(index: int) -> InlineKeyboardMarkup:
    photos = create_examples_gallery()

    first = [[InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu'),
              InlineKeyboardButton(text='->', callback_data=f'gallery:next:{index + 1}')]]

    second = [[InlineKeyboardButton(text='<-', callback_data=f'gallery:prev:{index - 1}'),
               InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu'),
               InlineKeyboardButton(text='->', callback_data=f'gallery:next:{index + 1}')]]

    third = [[InlineKeyboardButton(text='<-', callback_data=f'gallery:prev:{index - 1}'),
              InlineKeyboardButton(text='Назад в меню', callback_data='back_to_menu')]]

    if index == 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=first)

    elif index == len(photos) - 1:
        keyboard = InlineKeyboardMarkup(inline_keyboard=third)

    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=second)

    return keyboard


# Здесь заканчивается блок кода с функциями для класса MainMenuCallback

# Отсюда начинается блок кода с функциями для класса PersonalAccountCallback

def create_order_history_keyboard_and_text(orders: List[Order] | None):
    if not orders:
        return "У вас пока нет заказов.", BackToPersonalMenu

    caption = 'Ваши заказы\n\n'
    keyboard = []
    buttons_per_row = 3

    for order in orders:
        order_date = order.order_date.strftime('%Y.%m.%d %H:%M:%S')
        caption += f"Заказ №{order.order_id} - - - от {order_date}\n"

    for i in range(0, len(orders), buttons_per_row):
        row = [
            InlineKeyboardButton(
                text=f"Открыть заказ №{order.order_id}",
                callback_data=f"view_order_{order.order_id}"
            )
            for order in orders[i:i + buttons_per_row]
        ]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")])

    return caption, InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_order_details(order):
    if not order:
        return "Заказ не найден."

    order_details = f"Заказ №{order.order_id}\n"
    order_details += f"Дата заказа: {order.order_date}\n"
    order_details += f"Статус: {order.status.name}\n\n"

    order_details += "Состав заказа:\n"
    total_price = 0

    for order_item in order.order_items:
        product = order_item.product
        product_name = product.name if product else "Неизвестный продукт"
        order_details += (
            f"  - {product_name} ({order_item.product_type.name}): "
            f"{order_item.quantity} шт. по {order_item.price} руб. за шт.\n"
        )

    order_details += f"\nИтого: {order.total_price} руб.\n"
    return order_details


# Здесь заканчивается блок кода с функциями для класса PersonalAccountCallback

# Здесь Начинается блок кода с функциями для класса CatalogCallback

def create_products_keyboard(page_num: int, products: List[Product], product_type: str) -> InlineKeyboardMarkup:
    max_buttons = 15
    buttons_per_row = 4 if len(products) % 4 == 0 else 3

    start_index = (page_num - 1) * max_buttons
    end_index = min(start_index + max_buttons, len(products))
    products_to_display = products[start_index:end_index]

    keyboard = []
    for i in range(0, len(products_to_display), buttons_per_row):
        row = [
            InlineKeyboardButton(
                text=str(j + 1 + start_index),
                callback_data=f'view_product_{product_type}_{products_to_display[j].product_id}'
            )
            for j in range(i, min(i + buttons_per_row, len(products_to_display)))
        ]
        keyboard.append(row)

    navigation_row = []
    if page_num > 1:
        navigation_row.append(InlineKeyboardButton(text='<-', callback_data=f'prev_page_{product_type}_{page_num - 1}'))
    if end_index < len(products):
        navigation_row.append(InlineKeyboardButton(text='->', callback_data=f'next_page_{product_type}_{page_num + 1}'))
    if navigation_row:
        keyboard.append(navigation_row)

    keyboard.append([InlineKeyboardButton(text='Назад в каталог', callback_data='back_to_catalog')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_products_list(products: List[Product]) -> str:
    return "\n".join([f"{i + 1}. {product.name}" for i, product in enumerate(products)])


def create_flowers_list(flowers: List[Product]) -> str:
    return "\n".join([f"{i + 1} - {flower.name}" for i, flower in enumerate(flowers)])


def create_product_keyboard(product_id: int, product_type: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{product_id}")],
            [InlineKeyboardButton(text="Назад к выбору", callback_data=f"{product_type.name}s")],
        ]
    )

# Здесь заканчивается блок кода с функциями для класса CatalogCallback


# Здесь Начинается блок кода с функциями для класса ShoppingCartAndOrdersCallback

def create_cart_list(cart_items):
    total_sum = 0
    cart_text = []

    for index, (cart, product) in enumerate(cart_items, start=1):
        item_sum = product.price * cart.count
        total_sum += item_sum
        cart_text.append(
            f"{index}. {product.name} — Количество: {cart.count} шт. — Цена: {product.price} руб. — Сумма: {item_sum} руб."
        )

    cart_text.append(f"\nОбщая сумма: {total_sum} руб.")
    return "\n".join(cart_text)


def create_cart_keyboard(page_num: int, cart_items, max_buttons=10):
    buttons_per_row = 3
    start_index = (page_num - 1) * max_buttons
    end_index = min(start_index + max_buttons, len(cart_items))
    items_to_display = cart_items[start_index:end_index]

    keyboard = []

    for i in range(0, len(items_to_display), buttons_per_row):
        row = [
            InlineKeyboardButton(
                text=str(j + 1 + start_index),
                callback_data=f'cart_item_{items_to_display[j][0].product_id}'
            )
            for j in range(i, min(i + buttons_per_row, len(items_to_display)))
        ]
        keyboard.append(row)

    navigation_row = []
    if page_num > 1:
        navigation_row.append(InlineKeyboardButton(text='<-', callback_data=f'prev_page_cart_{page_num - 1}'))
    if end_index < len(cart_items):
        navigation_row.append(InlineKeyboardButton(text='->', callback_data=f'next_page_cart_{page_num + 1}'))
    if navigation_row:
        keyboard.append(navigation_row)

    keyboard.append([InlineKeyboardButton(text='Оформить заказ', callback_data='place_order')])
    keyboard.append([InlineKeyboardButton(text='Назад в каталог', callback_data='back_to_catalog')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_cart_item_keyboard(product_id: int, count: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить количество", callback_data=f"change_quantity_{product_id}_{count}"),
                InlineKeyboardButton(text="Удалить из корзины", callback_data=f"remove_from_cart_{product_id}")
            ],
            [
                InlineKeyboardButton(text="Назад в корзину", callback_data="shopping_cart"),
            ]
        ]
    )


def generate_quantity_keyboard(product_id: int, curr_count: int) -> InlineKeyboardMarkup:
    increase_buttons = [
        InlineKeyboardButton(text="+1", callback_data=f"increase_quantity_{product_id}_1"),
        InlineKeyboardButton(text="+2", callback_data=f"increase_quantity_{product_id}_2"),
        InlineKeyboardButton(text="+5", callback_data=f"increase_quantity_{product_id}_5"),
    ]

    decrease_buttons = []
    if curr_count >= 2:
        decrease_buttons.append(
            InlineKeyboardButton(text="-1", callback_data=f"decrease_quantity_{product_id}_1")
        )
    if curr_count >= 3:
        decrease_buttons.append(
            InlineKeyboardButton(text="-2", callback_data=f"decrease_quantity_{product_id}_2")
        )
    if curr_count > 5:
        decrease_buttons.append(
            InlineKeyboardButton(text="-5", callback_data=f"decrease_quantity_{product_id}_5")
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            increase_buttons,
            decrease_buttons if decrease_buttons else [],
            [InlineKeyboardButton(text="Назад к товару", callback_data=f"cart_item_{product_id}")],
        ]
    )

# Здесь заканчивается блок кода с функциями для класса ShoppingCartAndOrdersCallback


# Здесь начинается блок кода с функциями для класса PlaceOrderCallback

def create_addresses_keyboard(addresses: List[Addresses]) -> Tuple[str, InlineKeyboardMarkup]:
    text_lines = ["Выберите адрес для заказа:"]
    keyboard_buttons = []

    for idx, address in enumerate(addresses, start=1):
        description = (
            f"{idx}. {address.city}, {address.address_line}"
        )
        text_lines.append(description)

        keyboard_buttons.append([
            InlineKeyboardButton(text=f"Выбрать адрес {idx}",
                                 callback_data=f"select_address_{address.address_id}")
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(text="Вернуться в корзину", callback_data="shopping_cart")
    ])

    caption = "\n\n".join(text_lines)
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    return caption, keyboard


def create_order_confirmation(cart_items, address: Addresses, customer: Customer) -> Tuple[str, InlineKeyboardMarkup]:
    total_sum = 0
    cart_text = []

    for index, (cart, product) in enumerate(cart_items, start=1):
        item_sum = product.price * cart.count
        total_sum += item_sum
        cart_text.append(
            f"{index}. {product.name} — Количество: {cart.count} шт. — Цена: {product.price} руб. — Сумма: {item_sum} руб."
        )

    cart_text.append(f"\nОбщая сумма: {total_sum} руб.")

    address_text = f"\n\nВыбранный адрес:\n{address.city}, {address.address_line}"

    receiver = (f"\n\nПолучатель: {address.recipient_name if address.recipient_name else customer.first_name}, Телефон: "
                f"{address.recipient_number if address.recipient_name else customer.phone}")

    caption = "\n".join(cart_text) + address_text + receiver

    keyboard_buttons = [
        [InlineKeyboardButton(text="Перейти к оплате", callback_data=f"proceed_to_payment_{address.address_id}")],
        [InlineKeyboardButton(text="Изменить получателя", callback_data=f"change_recipient_{address.address_id}")],
        [InlineKeyboardButton(text="Вернуться в корзину", callback_data="shopping_cart")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    return caption, keyboard

# Здесь заканчивается блок кода с функциями для класса PlaceOrderCallback


def get_admin_id() -> int:
    return 5273759076


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Вызвать главное меню"),
        BotCommand(command="/faq", description="Что может этот бот (FAQ)")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())