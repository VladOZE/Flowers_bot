from typing import Tuple, List
from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, BotCommandScopeDefault
from src.database.models import *
import os


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

# Здесь заканчивается блок кода с функциями для класса PersonalAccountCallback


# Здесь заканчивается блок кода с функциями для класса CatalogCallback
def create_flowers_keyboard(page_num: int, flowers: List[Product]) -> InlineKeyboardMarkup:
    max_buttons = 15
    buttons_per_row = 4

    start_index = (page_num - 1) * max_buttons
    end_index = start_index + max_buttons
    flowers_to_display = flowers[start_index:end_index]

    keyboard = []
    for i in range(0, len(flowers_to_display), buttons_per_row):
        row = [
            InlineKeyboardButton(
                text=f"{j + 1 + start_index}",
                callback_data=f"flower_{flowers_to_display[j].product_id}"
            )
            for j in range(i, min(i + buttons_per_row, len(flowers_to_display)))
        ]
        keyboard.append(row)

    navigation_row = []
    if start_index > 0:
        navigation_row.append(InlineKeyboardButton(text='<-', callback_data=f'flowers_prev_page_{page_num - 1}'))
    if end_index < len(flowers):
        navigation_row.append(InlineKeyboardButton(text='->', callback_data=f'flowers_next_page_{page_num + 1}'))

    if navigation_row:
        keyboard.append(navigation_row)

    keyboard.append([InlineKeyboardButton(text='Назад в каталог', callback_data='back_to_catalog')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_flowers_list(flowers: List[Product]) -> str:
    return "\n".join([f"{i + 1} - {flower.name}" for i, flower in enumerate(flowers)])

# Здесь заканчивается блок кода с функциями для класса CatalogCallback


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Вызвать главное меню"),
        BotCommand(command="/faq", description="Что может этот бот (FAQ)")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())