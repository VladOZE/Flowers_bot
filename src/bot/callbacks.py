from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import Router, F
from functions import *
from keyboards import *
from quaries import *
from states import SupportStates
from aiogram.fsm.context import FSMContext


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
        self.router.callback_query(F.data == "back_to_menu_from_text")(self.back_to_menu_from_text)


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

    async def back_to_menu_from_text(self, callback: CallbackQuery):
        await callback.message.delete()
        text, path = main_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.answer_photo(photo=photo, reply_markup=StartMenu)


class PersonalAccountCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "mailing")(self.mailing)
        self.router.callback_query(F.data.startswith("mailing:"))(self.turn_mailing)
        self.router.callback_query(F.data == "appeals")(self.appeals)

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

    async def appeals(self, callback: CallbackQuery):
        user = callback.from_user
        _, path = personal_account_menu_text()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть открытые обращения", callback_data=f"open_appeals_{user.id}")],
            [InlineKeyboardButton(text="Посмотреть закрытые обращения", callback_data=f"closed_appeals_{user.id}")],
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_menu")]
        ])
        caption = 'Выберете какой тип обращений вы хотите посмотреть!'
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=keyboard)


class SupportCallback:
    def __init__(self, router: Router, admin_id: int):
        self.router = router
        self.register_callbacks()
        self.admin_id = admin_id

    def register_callbacks(self):
        self.router.callback_query(F.data == "call_operator")(self.call_operator)
        self.router.message(SupportStates.Question)(self.answer_question)
        self.router.message(Command('reply'))(self.admin_reply)
        self.router.callback_query(F.data.startswith("close_"))(self.close_ticket)
        self.router.callback_query(F.data.startswith("add_"))(self.add_text_ticket)
        self.router.message(SupportStates.AddMessage)(self.handle_ticket_message)
        self.router.callback_query(F.data.startswith("open_appeals_"))(self.show_open_appeals)
        self.router.callback_query(F.data.startswith("closed_appeals_"))(self.show_closed_appeals)
    #    self.router.callback_query(F.data.startswith("feedback_form"))(self.feedback_form)

    async def call_operator(self, callback: CallbackQuery, state: FSMContext):
        text, path = support_menu_text()
        user = callback.from_user
        caption = 'Напишите ваш вопрос, он будет доставлен модератору'
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        message = await callback.message.edit_media(photo, reply_markup=BackToMenu)
        await state.update_data(message_id=message.message_id)
        await state.set_state(SupportStates.Question)

    async def answer_question(self, message: Message, state: FSMContext):
        customer_telegram_id = message.from_user.id
        user_question = message.text
        await message.delete()

        data = await state.get_data()
        bot_message_id = data.get('message_id')

        ticket_id = data.get('ticket_id')
        if not ticket_id:
            ticket = create_ticket(customer_telegram_id=customer_telegram_id)
            ticket_id = ticket.ticket_id
            await state.update_data(ticket_id=ticket_id)

        add_message_to_ticket(message_id=message.message_id, ticket_id=ticket_id, sender_type='user', text=message.text)

        await message.bot.send_message(self.admin_id, f"ID вопроса: {ticket_id}\n"
                                                          f"Вопрос от {message.from_user.full_name} ({message.from_user.id}):\n{user_question}\n\n"
                                                          f"Для ответа используйте /reply 'ID вопроса' 'ваш ответ'")

        _, path = support_menu_text()
        new_caption = "Ваше сообщение успешно доставлено модератору"

        await message.bot.edit_message_media(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            media=InputMediaPhoto(media=FSInputFile(path), caption=new_caption),
            reply_markup=BackToMenu
        )

        await state.clear()

    async def admin_reply(self, message: Message):
        if message.from_user.id != self.admin_id:
            return

        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply("Неверный формат команды. Используйте /reply ID тикета ваш ответ.")
            return
        ticket_id = int(args[1])
        reply_text = args[2]

        ticket = get_ticket_by_id(ticket_id)
        if not ticket:
            await message.reply(f"Тикет с ID {ticket_id} не найден.")
            return

        add_message_to_ticket(
            message_id=message.message_id,
            ticket_id=ticket_id,
            sender_type="admin",
            text=reply_text
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                InlineKeyboardButton(text='Закрыть обращение', callback_data=f"close_{ticket_id}_{message.from_user.id}"),
                InlineKeyboardButton(text='Дополнить обращение', callback_data=f"add_{ticket_id}_{message.from_user.id}")
                ]
            ]
        )

        await message.bot.send_message(
            chat_id=ticket.customer_telegram_id,
            text=f"Ваш вопрос:\n{ticket.messages[-1].message_text}\n\n"
                 f"Ответ администратора:\n{reply_text}", reply_markup=keyboard
        )

        await message.reply("Ваш ответ доставлен пользователю!")

    async def close_ticket(self, callback: CallbackQuery):
        ticket_id = int(callback.data.split("_")[1])
        if get_ticket_by_id(ticket_id):
            set_ticket_status_closed(ticket_id)
        await callback.message.edit_text('Обращение успешно закрыто!', reply_markup=BackToMenuFromText)

    async def add_text_ticket(self, callback: CallbackQuery, state: FSMContext):
        data = callback.data.split("_")
        ticket_id = int(data[1])
        customer_id = int(data[2])

        ticket = get_ticket_by_id(ticket_id)
        if not ticket:
            await callback.message.edit_text("Обращение не найдено.", reply_markup=BackToMenuFromText)
            return

        if ticket.status == "closed":
            await callback.message.edit_text("Обращение уже закрыто, вы не можете дополнить его",
                                             reply_markup=BackToMenuFromText)
            return

        message = await callback.message.edit_text("Напишите ваш новый вопрос или комментарий:", reply_markup=BackToMenuFromText)

        await state.set_state(SupportStates.AddMessage)
        await state.update_data(ticket_id=ticket_id, customer_id=customer_id, message_id=message.message_id)

    async def handle_ticket_message(self, message: Message, state: FSMContext):
        data = await state.get_data()
        ticket_id = data.get("ticket_id")
        customer_id = data.get("customer_id")
        message_id = data.get("message_id")
        await message.delete()

        if not ticket_id or not customer_id:
            await message.edit_text("Произошла ошибка. Попробуйте снова.", reply_markup=BackToMenuFromText)
            await state.clear()
            return

        new_message = add_message_to_ticket(
            message_id=message.message_id,
            ticket_id=ticket_id,
            sender_type="user",
            text=message.text,
        )

        admin_text = (
            f"Новое сообщение в тикете №{ticket_id} от пользователя {message.from_user.full_name}:\n"
            f"{message.text}\n\n"
            f"Вы можете ответить командой: /reply ID тикета ваш ответ"
        )
        await message.bot.send_message(self.admin_id, admin_text)

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text='Ваше сообщение успешно доставлено администратору!',
            reply_markup=BackToMenuFromText)
        await state.clear()

    # async def feedback_form(self, callback: CallbackQuery):

    async def show_open_appeals(self, callback: CallbackQuery):
        customer_id = callback.from_user.id
        _, path = main_menu_text()

        tickets = get_customer_tickets(customer_id, 'open')

        if not tickets:
            caption = "У вас нет открытых обращений."
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            await callback.message.edit_media(media=photo, reply_markup=BackToMenu)
            return

        caption = "Ваши открытые обращения:\n\n"
        keyboard = []

        buttons = [
            InlineKeyboardButton(
                text=f"Открыть №{ticket.ticket_id}",
                callback_data=f"view_ticket_{ticket.ticket_id}"
            )
            for ticket in tickets
        ]

        for i in range(0, len(buttons), 3):
            keyboard.append(buttons[i:i + 3])

        keyboard.append(
            [InlineKeyboardButton(text="Назад в главное меню", callback_data="back_to_menu")]
        )

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=reply_markup)


    async def show_closed_appeals(self, callback: CallbackQuery):
        customer_id = callback.from_user.id
        tickets = get_customer_tickets(customer_id, 'closed')


class CatalogCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "back_to_catalog")(self.back_to_catalog)
        self.router.callback_query(F.data == "flowers")(self.flowers)
        self.router.callback_query(F.data.startswith("flowers_prev_page_"))(self.flowers_prev_page)
        self.router.callback_query(F.data.startswith("flowers_next_page_"))(self.flowers_next_page)
        self.router.callback_query(F.data == "bouquets")(self.bouquets)
        self.router.callback_query(F.data == "toys")(self.toys)
        self.router.callback_query(F.data == "personal_order")(self.personal_order)
        self.router.callback_query(F.data == "shopping_cart")(self.shopping_cart)

    async def back_to_catalog(self, callback:CallbackQuery):
        text, path = catalog_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=CatalogMenu)

    async def flowers(self, callback: CallbackQuery):
        _, path = catalog_menu_text()
        flowers = get_flowers_list()
        if not flowers:
            caption = "Нет доступных цветов."
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            await callback.message.edit_media(media=photo, reply_markup=BackToMenu)
            return

        flowers_list = create_flowers_list(flowers)
        keyboard = create_flowers_keyboard(page_num=1, flowers=flowers)

        caption = f"Доступные цветы:\n\n{flowers_list}"
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=keyboard)

    async def flowers_next_page(self, callback: CallbackQuery):
        page_num = int(callback.data.split('_')[-1])
        flowers = get_flowers_list()

        keyboard = create_flowers_keyboard(page_num=page_num, flowers=flowers)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    async def flowers_prev_page(self, callback: CallbackQuery):
        page_num = int(callback.data.split('_')[-1])
        flowers = get_flowers_list()

        keyboard = create_flowers_keyboard(page_num=page_num, flowers=flowers)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    async def bouquets(self, callback: CallbackQuery):
        return

    async def toys(self, callback: CallbackQuery):
        return

    async def personal_order(self, callback: CallbackQuery):
        return

    async def shopping_cart(self, callback: CallbackQuery):
        return


MainMenuCallbackHandler = MainMenuCallback(router_callback)
PersonalAccountCallbackHandler = PersonalAccountCallback(router_callback)
SupportCallbackHandler = SupportCallback(router_callback, 5273759076)
CatalogCallbackHandler = CatalogCallback(router_callback)