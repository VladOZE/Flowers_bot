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
async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Вызвать главное меню"),
        BotCommand(command="/faq", description="Что может этот бот (FAQ)")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())