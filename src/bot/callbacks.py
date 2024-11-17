from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram import Router, F
from functions import *
from keyboards import *
from quaries import *


router_callback = Router()


class MainMenuCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "catalog")(self.catalog)
        self.router.callback_query(F.data == "support")(self.support)
        self.router.callback_query(F.data == "about")(self.about)
        self.router.callback_query(F.data == "personal_account")(self.personal_account)
        self.router.callback_query(F.data == "examples")(self.examples)
        self.router.callback_query(F.data.startswith("gallery:"))(self.navigate_gallery)
        self.router.callback_query(F.data == "back_to_menu")(self.back_to_menu)

    async def catalog(self, callback: CallbackQuery):
        text, path = catalog_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=CatalogMenu)

    async def support(self, callback: CallbackQuery):
        text, path = support_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=SupportMenu)

    async def about(self, callback: CallbackQuery):
        text, path = about_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=BackToMenu)

    async def personal_account(self, callback: CallbackQuery):
        text, path = personal_account_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=PersonalAccountMenu)

    async def examples(self, callback: CallbackQuery):
        index = 0
        gallery = create_examples_gallery()
        photo = FSInputFile(gallery[index])
        await callback.message.edit_media(media=InputMediaPhoto(media=photo), reply_markup=create_keyboard_for_gallery(index))

    async def navigate_gallery(self, callback: CallbackQuery):
        data = callback.data.split(':')
        action = data[1]
        index = int(data[2])
        images = create_examples_gallery()

        if action in ['prev', 'next']:
            photo = FSInputFile(images[index])
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo), reply_markup=create_keyboard_for_gallery(index))

    async def back_to_menu(self, callback: CallbackQuery):
        text, path = main_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=StartMenu)


class PersonalAccountCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "mailing")(self.mailing)
        self.router.callback_query(F.data.startswith("mailing:"))(self.turn_mailing)

    async def mailing(self, callback: CallbackQuery):
        text, path = personal_account_menu_text()
        user = callback.from_user
        mailing_status = get_customer_mailing(user.id)

        if mailing_status[0] == 1:
            caption = 'У вас включена рассылка, желаете ее выключить?'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выключить рассылку", callback_data=f"mailing:{user.id}:off")],
                [InlineKeyboardButton(text="Главное меню", callback_data="back_to_menu")]
            ])
        else:
            caption = 'У вас выключена рассылка, желаете ее включить?'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Включить рассылку", callback_data=f"mailing:{user.id}:on")],
                [InlineKeyboardButton(text="Главное меню", callback_data="back_to_menu")]
            ])
        await callback.message.edit_media(media=photo, reply_markup=keyboard)

    async def turn_mailing(self, callback: CallbackQuery):
        text, path = personal_account_menu_text()
        data = callback.data.split(':')
        user_id = int(data[1])
        command_type = data[2]
        session = Session()
        customer = session.query(Customer).filter(Customer.customer_telegram_id == user_id).first()

        if command_type == "off":
            caption = 'Рассылка успешно отключена!'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            customer.mailing = 0
            session.commit()
        else:
            caption = 'Рассылка успешно включена!'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            customer.mailing = 1
            session.commit()
        session.close()
        await callback.message.edit_media(media=photo, reply_markup=BackToMenu)


MainMenuCallbackHandler = MainMenuCallback(router_callback)
PersonalAccountCallbackHandler = PersonalAccountCallback(router_callback)