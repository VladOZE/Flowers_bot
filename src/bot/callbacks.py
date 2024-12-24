from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.filters import Command
from aiogram import Router, F
from functions import *
from keyboards import *
from quaries import *
from states import SupportStates, PersonalOrderStates, NewAddressStates, PersonalInfoStates, RecipientStates, FeedbackFormStates
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
        self.router.callback_query(F.data == "my_addresses")(self.my_addresses)
        self.router.callback_query(F.data == "new_address")(self.new_address)
        self.router.message(NewAddressStates.City)(self.process_city)
        self.router.message(NewAddressStates.AddressLine)(self.process_address_line)
        self.router.callback_query(F.data == "orders_history")(self.orders_history)
        self.router.callback_query(F.data.startswith("view_order_"))(self.view_order)


    async def mailing(self, callback: CallbackQuery):
        text, path = personal_account_menu_text()
        user = callback.from_user
        mailing_status = get_customer_mailing(user.id)

        if mailing_status[0] == 1:
            caption = 'У вас включена рассылка, желаете ее выключить?'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выключить рассылку", callback_data=f"mailing:{user.id}:off")],
                [InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")]
            ])
        else:
            caption = 'У вас выключена рассылка, желаете ее включить?'
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Включить рассылку", callback_data=f"mailing:{user.id}:on")],
                [InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")]
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
            [InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")]
        ])
        caption = 'Выберете какой тип обращений вы хотите посмотреть!'
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=keyboard)

    async def my_addresses(self, callback: CallbackQuery):
        customer_telegram_id = callback.from_user.id

        addresses = get_customer_addresses(customer_telegram_id)
        if not addresses:
            await callback.message.edit_caption(caption='Адреса не найдены, создадим новый?',
                                                reply_markup=NewAddressPersonal)
        addresses_text = "\n\n".join(
            [f"{idx}. Город: {a.city}\nАдрес: {a.address_line}"
             for idx, a in enumerate(addresses, 1)]
        )
        await callback.message.edit_caption(
            caption=f"Ваши адреса:\n\n{addresses_text}",
            reply_markup=NewAddressPersonal
        )

    async def new_address(self, callback: CallbackQuery, state: FSMContext):
        caption = "Введите название города для нового адреса (Например: 'Санкт-Петербург'):"
        message = await callback.message.edit_caption(caption=caption, reply_markup=BackToPersonalMenu)
        await state.update_data(message_id=message.message_id)
        await state.set_state(NewAddressStates.City)

    async def process_city(self, message: Message, state: FSMContext):
        await state.update_data(city=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data.get("message_id")

        caption = "Введите полный адрес с городом\n\n(Пример: 'г. Санкт-Петербург, ул. Пушкина, д.220 к.1 кв.300'):"
        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, caption=caption)
        await state.set_state(NewAddressStates.AddressLine)

    async def process_address_line(self, message: Message, state: FSMContext):
        await state.update_data(address_line=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data.get("message_id")
        city = data["city"]
        address_line = data["address_line"]

        customer_telegram_id = message.from_user.id
        customer = get_customer_by_telegram_id(customer_telegram_id)
        new_address = Addresses(
            customer_id=customer.customer_id,
            city=city,
            address_line=address_line
        )
        add_new_address(new_address)

        caption = f"Ваш адрес сохранён:\n\nГород: {city}\nАдрес: {address_line}"
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=caption,
            reply_markup=BackToPersonalMenu
        )
        await state.clear()

    async def orders_history(self, callback: CallbackQuery):
        customer_telegram_id = callback.from_user.id

        orders = get_user_orders(customer_telegram_id)
        caption, keyboard = create_order_history_keyboard_and_text(orders)

        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def view_order(self, callback: CallbackQuery):
        data = callback.data.split('_')
        order_id = data[-1]

        order_details = get_order_by_id(order_id)
        caption = create_order_details(order_details)

        await callback.message.edit_caption(caption=caption, reply_markup=BackToPersonalMenu)


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
        self.router.callback_query(F.data.startswith("add_ticketinfo_"))(self.add_text_ticket)
        self.router.message(SupportStates.AddMessage)(self.handle_ticket_message)
        self.router.callback_query(F.data.startswith("open_appeals_"))(self.show_open_appeals)
        self.router.callback_query(F.data.startswith("closed_appeals_"))(self.show_closed_appeals)
        self.router.callback_query(F.data.startswith("feedback_form"))(self.feedback_form)
        self.router.message(FeedbackFormStates.PhoneOrMail)(self.process_form_contact_info)
        self.router.message(FeedbackFormStates.FirstName)(self.process_form_name)
        self.router.message(FeedbackFormStates.Question)(self.process_form_question)
        self.router.callback_query(F.data.startswith("view_ticket_"))(self.view_ticket)

    async def call_operator(self, callback: CallbackQuery, state: FSMContext):
        text, path = support_menu_text()
        user = callback.from_user
        caption = 'Напишите ваш вопрос, он будет доставлен модератору'
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        message = await callback.message.edit_media(photo, reply_markup=BackToSupportMenu)
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
                InlineKeyboardButton(text='Дополнить обращение', callback_data=f"add_ticketinfo_{ticket_id}_{message.from_user.id}")
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
        ticket_id = int(data[2])
        customer_id = int(data[3])

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
            [InlineKeyboardButton(text="Назад к обращениям", callback_data="appeals")]
        )

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=reply_markup)

    async def show_closed_appeals(self, callback: CallbackQuery):
        customer_id = callback.from_user.id
        _, path = main_menu_text()

        tickets = get_customer_tickets(customer_id, 'closed')

        if not tickets:
            caption = "У вас нет закрытых обращений."
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            await callback.message.edit_media(media=photo, reply_markup=BackToMenu)
            return

        caption = "Ваши закрытые обращения:\n\n"
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
            [InlineKeyboardButton(text="Назад к обращениям", callback_data="appeals")]
        )

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=reply_markup)

    async def feedback_form(self, callback: CallbackQuery, state: FSMContext):
        caption = ("В этом разделе вы можете:\n\nКратко описать свой вопрос и оставить свои контактные данные для обратной связи\n\n"
                   "Опишите свою проблему в чате ниже:")

        message = await callback.message.edit_caption(caption=caption, reply_markup=BackToSupportMenu)

        await state.update_data(message_id=message.message_id)
        await state.set_state(FeedbackFormStates.Question)

    async def process_form_question(self, message: Message, state: FSMContext):
        await state.update_data(question=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data["message_id"]

        caption = "Введите как к вам обращаться:"
        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, caption=caption, reply_markup=BackToSupportMenu)
        await state.set_state(FeedbackFormStates.FirstName)

    async def process_form_name(self, message: Message, state: FSMContext):
        await state.update_data(first_name=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data["message_id"]

        caption = ("Введите данные для связи:\n\n"
                   "1. Телефон в любом формате\n\n"
                   "2. Email формата xxxxx@xxx.xx")
        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, caption=caption,
                                               reply_markup=BackToSupportMenu)
        await state.set_state(FeedbackFormStates.PhoneOrMail)

    async def process_form_contact_info(self, message: Message, state: FSMContext):
        await state.update_data(mail_or_phone=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data["message_id"]
        question = data["question"]
        first_name = data["first_name"]
        contact_info = data["mail_or_phone"]
        customer_telegram_id = message.from_user.id
        customer_name = message.from_user.first_name


        caption_for_user = ("Ваш запрос отправлен!")
        text_for_admin = (f"Запрос на обратную связь от {customer_name} ({customer_telegram_id})\n\n"
                          f"Вопрос: {question}\n\n"
                          f"Имя для обращения: {first_name}\n\n"
                          f"Где связаться: {contact_info}")

        await message.bot.send_message(self.admin_id, text=text_for_admin)

        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id,
                                               caption=caption_for_user, reply_markup=BackToSupportMenu)

        await state.clear()

    async def view_ticket(self, callback: CallbackQuery):
        data = callback.data.split('_')
        ticket_id = data[-1]

        messages = get_ticket_messages(ticket_id)
        caption = "\n\n".join(
            [f"{message.created_at} сообщение от {'поддержки' if message.sender_type == SupportSenderType.admin else 'вас'}: {message.message_text}"
             for message in messages]
        )

        await callback.message.edit_caption(caption=caption, reply_markup=BackToAppeals)






class CatalogCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "back_to_catalog")(self.back_to_catalog)
        self.router.callback_query(F.data == "flowers")(self.handle_flowers)
        self.router.callback_query(F.data == "bouquets")(self.handle_bouquets)
        self.router.callback_query(F.data == "toys")(self.handle_toys)
        self.router.callback_query(F.data.startswith("flowers_prev_page_"))(self.handle_flowers_prev_page)
        self.router.callback_query(F.data.startswith("flowers_next_page_"))(self.handle_flowers_next_page)
        self.router.callback_query(F.data.startswith("bouquets_prev_page_"))(self.handle_bouquets_prev_page)
        self.router.callback_query(F.data.startswith("bouquets_next_page_"))(self.handle_bouquets_next_page)
        self.router.callback_query(F.data.startswith("toys_prev_page_"))(self.handle_toys_prev_page)
        self.router.callback_query(F.data.startswith("toys_next_page_"))(self.handle_toys_next_page)
        self.router.callback_query(F.data.startswith("view_product_"))(self.view_product)
        self.router.callback_query(F.data == "personal_order")(self.personal_order)
        self.router.message(PersonalOrderStates.Description)(self.personal_order_description)
        self.router.message(PersonalOrderStates.Photo)(self.personal_order_photo)
        self.router.callback_query(F.data == "send_personal_order")(self.send_personal_order)
        self.router.callback_query(F.data.startswith("back_to_catalog_personal_order_"))(self.back_to_catalog_personal_order)


    async def back_to_catalog(self, callback:CallbackQuery):
        text, path = catalog_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=CatalogMenu)

    async def products(self, callback: CallbackQuery, product_type: str):
        _, path = catalog_menu_text()
        products = get_products_list(product_type)
        if not products:
            caption = "К сожалению на данный момент каталог пуст"
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            await callback.message.edit_media(media=photo, reply_markup=BackToCatalog)
            return

        products_list = create_products_list(products)
        keyboard = create_products_keyboard(page_num=1, products=products, product_type=product_type)

        caption = products_list
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=keyboard)

    async def products_next_page(self, callback: CallbackQuery, product_type: str):
        page_num = int(callback.data.split('_')[-1])
        products = get_products_list(product_type)

        keyboard = create_products_keyboard(page_num=page_num, products=products, product_type=product_type)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    async def products_prev_page(self, callback: CallbackQuery, product_type: str):
        page_num = int(callback.data.split('_')[-1])
        products = get_products_list(product_type)

        keyboard = create_products_keyboard(page_num=page_num, products=products, product_type=product_type)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    async def handle_flowers(self, callback: CallbackQuery):
        await self.products(callback, product_type='flower')

    async def handle_bouquets(self, callback: CallbackQuery):
        await self.products(callback, product_type='bouquet')

    async def handle_toys(self, callback: CallbackQuery):
        await self.products(callback, product_type='toy')

    async def handle_flowers_next_page(self, callback: CallbackQuery):
        await self.products_next_page(callback, product_type='flower')

    async def handle_flowers_prev_page(self, callback: CallbackQuery):
        await self.products_prev_page(callback, product_type='flower')

    async def handle_bouquets_next_page(self, callback: CallbackQuery):
        await self.products_next_page(callback, product_type='bouquet')

    async def handle_bouquets_prev_page(self, callback: CallbackQuery):
        await self.products_prev_page(callback, product_type='bouquet')

    async def handle_toys_next_page(self, callback: CallbackQuery):
        await self.products_next_page(callback, product_type='toy')

    async def handle_toys_prev_page(self, callback: CallbackQuery):
        await self.products_prev_page(callback, product_type='toy')

    async def view_product(self, callback: CallbackQuery):
        product_id = int(callback.data.split('_')[-1])

        product = get_product_by_id(product_id)
        if not product:
            await callback.answer("Товар не найден.")
            return

        if product.description:
            caption = f"Название: {product.name}\n\n{product.description}\n\nЦена: {product.price} ₽"
        else:
            caption = f"Название: {product.name}\n\nЦена: {product.price} ₽"

        if product.image_url:
            photo = InputMediaPhoto(media=product.image_url, caption=caption)
        else:
            # Тут надо будет заменить изображение
            _, path = catalog_menu_text()
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)

        await callback.message.edit_media(media=photo, reply_markup=create_product_keyboard(product.product_id, product.product_type))

    async def personal_order(self, callback: CallbackQuery, state: FSMContext):
        _, path = catalog_menu_text()
        caption = (
            'В этом разделе вы можете подробно описать, какой букет вы хотите.\n\n'
            'Сначала напишите текст с описанием ваших пожеланий, например:\n\n'
            '"Я хочу букет из 15 роз с красными лентами".\n\n'
            'После этого вы сможете прикрепить фото или отправить заказ без фото.\n\n'
            'Напишите текст в чат ниже, чтобы продолжить.'
        )
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)

        message = await callback.message.edit_media(photo, reply_markup=BackToCatalog)

        await state.update_data(message_id=message.message_id)
        await state.set_state(PersonalOrderStates.Description)

    async def personal_order_description(self, message: Message, state: FSMContext):
        await state.update_data(order_description=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data.get("message_id")

        order = create_personal_order(
            telegram_id=message.from_user.id,
            description=message.text,
            photo_path=None,
            status="accepted"
        )

        order_id = order.personal_order_id
        await state.update_data(order_id=order_id)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отправить", callback_data="send_personal_order")],
                [InlineKeyboardButton(text="Назад в каталог",
                                      callback_data=f"back_to_catalog_personal_order_{order_id}")]
            ]
        )

        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=(
                'Ваше описание сохранено. Если вы хотите прикрепить фотографию, отправьте её сейчас.\n\n'
                'Или нажмите кнопку "Отправить", чтобы завершить заказ без фото.'
            ),
            reply_markup=keyboard
        )

        await state.set_state(PersonalOrderStates.Photo)

    async def personal_order_photo(self, message: Message, state: FSMContext):
        path = '../images/personal_order/'

        data = await state.get_data()
        order_id = data.get("order_id")
        message_id = data.get("message_id")

        os.makedirs(path, exist_ok=True)

        photo = message.photo[-1]

        unique_filename = f"personal_order_{order_id}.jpg"
        file_path = os.path.join(path, unique_filename)

        await message.bot.download(file=photo, destination=file_path)

        await state.update_data(photo_path=file_path)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
        [InlineKeyboardButton(text="Отправить", callback_data="send_personal_order")],
        [InlineKeyboardButton(text="Назад в каталог", callback_data=f"back_to_catalog_personal_order_{order_id}")]
    ])

        await message.delete()
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=("Ваше фото успешно сохранено! Нажмите 'Отправить', чтобы завершить заказ, или отмените его."),
            reply_markup=keyboard)

        await state.set_state(PersonalOrderStates.Confirmation)

    async def send_personal_order(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        order_id = data.get("order_id")
        order_description = data.get("order_description")
        photo_path = data.get("photo_path")
        message_id = data.get("message_id")

        order = update_personal_order(
            personal_order_id=order_id,
            description=order_description,
            photo_path=photo_path,
            status='accepted'
        )

        admin_chat_id = get_admin_id()

        message_text = (
            f"Новый заказ от {callback.from_user.full_name} "
            f"(@{callback.from_user.username or 'Не указано'}):\n\n"
            f"{order.description}"
        )

        if order.image:
            photo = FSInputFile(photo_path)
            await callback.bot.send_photo(chat_id=admin_chat_id, photo=photo, caption=message_text)

        else:
            await callback.bot.send_message(chat_id=admin_chat_id, text=message_text)

        await callback.bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=message_id,
            caption="Ваш заказ отправлен! Спасибо за обращение.",
            reply_markup=BackToCatalog)

        await state.clear()

    async def back_to_catalog_personal_order(self, callback: CallbackQuery):
        personal_order_id = int(callback.data.split('_')[-1])
        set_personal_order_status_closed(personal_order_id)
        text, path = catalog_menu_text()
        photo = InputMediaPhoto(media=FSInputFile(path), caption=text)
        await callback.message.edit_media(photo, reply_markup=CatalogMenu)


class ShoppingCartAndOrdersCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data.startswith("add_to_cart_"))(self.add_to_cart)
        self.router.callback_query(F.data == "shopping_cart")(self.shopping_cart)
        self.router.callback_query(F.data.startswith("next_page_cart_"))(self.next_page)
        self.router.callback_query(F.data.startswith("prev_page_cart_"))(self.previous_page)
        self.router.callback_query(F.data.startswith("cart_item_"))(self.view_cart_item)
        self.router.callback_query(F.data.startswith("change_quantity_"))(self.change_quantity)
        self.router.callback_query(F.data.startswith("increase_quantity_"))(self.increase_quantity)
        self.router.callback_query(F.data.startswith("decrease_quantity_"))(self.decrease_quantity)
        self.router.callback_query(F.data.startswith("remove_from_cart_"))(self.remove_from_cart)

    async def add_to_cart(self, callback:CallbackQuery):
        product_id = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        existing_cart_item = get_existing_cart_item(customer_telegram_id, product_id)
        if existing_cart_item:
            caption = 'Товар уже в корзине (изменить кол-во вы можете в корзине)'
        else:
            add_to_shopping_cart(customer_telegram_id, product_id)
            caption = 'Товар успешно добавлен в корзину!'

        await callback.message.edit_caption(caption=caption, reply_markup=BackToCatalog)

    async def shopping_cart(self, callback: CallbackQuery):
        customer_telegram_id = callback.from_user.id

        shopping_cart_items = get_customer_shopping_cart(customer_telegram_id)

        if not shopping_cart_items:
            await callback.message.edit_caption(caption="Ваша корзина пуста. Вы можете добавить товары из каталога.", reply_markup=BackToCatalog)
            return

        text = create_cart_list(shopping_cart_items)
        keyboard = create_cart_keyboard(page_num=1, cart_items=shopping_cart_items)

        await callback.message.edit_caption(caption=text, reply_markup=keyboard)

    async def next_page(self, callback: CallbackQuery):
        page_num = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        shopping_cart_items = get_customer_shopping_cart(customer_telegram_id)
        text = create_cart_list(shopping_cart_items, page_num)
        keyboard = create_cart_keyboard(page_num=page_num, cart_items=shopping_cart_items)

        await callback.message.edit_caption(caption=text, reply_markup=keyboard)

    async def previous_page(self, callback: CallbackQuery):
        page_num = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        shopping_cart_items = get_customer_shopping_cart(customer_telegram_id)
        text = create_cart_list(shopping_cart_items, page_num)
        keyboard = create_cart_keyboard(page_num=page_num, cart_items=shopping_cart_items)

        await callback.message.edit_caption(caption=text, reply_markup=keyboard)

    async def view_cart_item(self, callback: CallbackQuery):
        product_id = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        cart_item = get_existing_cart_item(customer_telegram_id, product_id)
        if not cart_item:
            await callback.answer("Товар не найден в корзине.")
            return

        product = get_product_by_id(product_id)
        if not product:
            await callback.answer("Информация о товаре недоступна.")
            return

        caption = (
            f"Название: {product.name}\n"
            f"Количество: {cart_item.count}\n"
            f"Цена за единицу: {product.price} ₽\n"
            f"Общая стоимость: {product.price * cart_item.count} ₽"
        )

        if product.image_url:
            photo = InputMediaPhoto(media=product.image_url, caption=caption)
        else:
            _, path = catalog_menu_text()
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)

        await callback.message.edit_media(media=photo, reply_markup=create_cart_item_keyboard(product_id, cart_item.count))

    async def change_quantity(self, callback: CallbackQuery):
        curr_count = int(callback.data.split('_')[-1])
        product_id = int(callback.data.split('_')[-2])
        product = get_product_by_id(product_id)
        if not product:
            await callback.answer("Информация о товаре недоступна.")
            return
        caption = (f'Товар: {product.name},\n\nТекущее кол-во: {curr_count}\n\n'
                   'Выберите насколько хотите изменить кол-во:')

        keyboard = generate_quantity_keyboard(product_id, curr_count)

        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def increase_quantity(self, callback: CallbackQuery):
        product_id = int(callback.data.split('_')[-2])
        delta = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        new_quantity = update_cart_item_quantity(customer_telegram_id, product_id, delta)
        product = get_product_by_id(product_id)
        caption = (f'Товар: {product.name},\n\nТекущее кол-во: {new_quantity}\n\n'
                    'Выберите насколько хотите изменить кол-во:')
        keyboard = generate_quantity_keyboard(product_id, new_quantity)
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def decrease_quantity(self, callback: CallbackQuery):
        product_id = int(callback.data.split('_')[-2])
        delta = -int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        new_quantity = update_cart_item_quantity(customer_telegram_id, product_id, delta)
        product = get_product_by_id(product_id)
        caption = (f'Товар: {product.name},\n\nТекущее кол-во: {new_quantity}\n\n'
                   'Выберите насколько хотите изменить кол-во:')
        keyboard = generate_quantity_keyboard(product_id, new_quantity)
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def remove_from_cart(self, callback:CallbackQuery):
        product_id = int(callback.data.split('_')[-1])
        customer_telegram_id = callback.from_user.id

        remove_from_cart(customer_telegram_id, product_id)

        cart_items = get_customer_shopping_cart(customer_telegram_id)
        if not cart_items:
            _, path = catalog_menu_text()
            caption = "Ваша корзина пуста. Вы можете добавить товары из каталога."
            photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
            await callback.message.edit_media(media = photo, reply_markup=BackToCatalog)
        else:
            cart_text = "Корзина успешно обновлена!"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться в корзину", callback_data=f"shopping_cart")]])
            await callback.message.edit_caption(caption=cart_text, reply_markup=keyboard)


class PlaceOrderCallback:
    def __init__(self, router: Router):
        self.router = router
        self.register_callbacks()

    def register_callbacks(self):
        self.router.callback_query(F.data == "place_order")(self.place_order)
        self.router.callback_query(F.data == "add_personal_info")(self.add_personal_info)
        self.router.callback_query(F.data.startswith("select_address_"))(self.select_address)
        self.router.message(PersonalInfoStates.FirstName)(self.process_name)
        self.router.message(PersonalInfoStates.PhoneNumber)(self.process_phone)
        self.router.callback_query(F.data.startswith("change_recipient_"))(self.change_recipient)
        self.router.callback_query(F.data.startswith("new_recipient_"))(self.new_recipient)
        self.router.message(RecipientStates.FirstName)(self.process_recipient_name)
        self.router.message(RecipientStates.PhoneNumber)(self.process_recipient_phone)
        self.router.callback_query(F.data.startswith("set_recipient_customer_"))(self.set_recipient_customer)
        self.router.callback_query(F.data.startswith("proceed_to_payment_"))(self.proceed_to_payment)
        self.router.callback_query(F.data.startswith("confirm_order_"))(self.confirm_order)

    async def place_order(self, callback: CallbackQuery):
        customer_telegram_id = callback.from_user.id

        customer = get_customer_by_telegram_id(customer_telegram_id)
        addresses = get_customer_addresses(customer_telegram_id)

        if not customer.real_name or not customer.phone:
            await callback.message.edit_caption(caption='Мне не хватает твоих данных для оформления заказа, заполним их?',
                                                reply_markup=AddPersonalInfo)

        elif not addresses:
            await callback.message.edit_caption(caption='Для оформления заказа необходимо заполнить адрес',
                                                reply_markup=NewAddressCart)

        else:
            caption, keyboard = create_addresses_keyboard(addresses)
            await callback.message.edit_caption(caption=caption,
                                                reply_markup=keyboard)

    async def add_personal_info(self, callback: CallbackQuery, state: FSMContext):
        caption = "Пожалуйста введите свое полное имя\n(например: 'Владислав')"
        message = await callback.message.edit_caption(caption=caption, reply_markup=BackToCart)
        await state.update_data(message_id=message.message_id)
        await state.set_state(PersonalInfoStates.FirstName)

    async def process_name(self, message: Message, state: FSMContext):
        await state.update_data(first_name=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data.get("message_id")

        caption = "Введите свой номер телефона в любом формате (например: '+79313521920':"
        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, caption=caption)
        await state.set_state(PersonalInfoStates.PhoneNumber)

    async def process_phone(self, message: Message, state: FSMContext):
        await state.update_data(phone_number=message.text)
        await message.delete()

        data = await state.get_data()
        message_id = data.get("message_id")
        real_name = data["first_name"]
        phone_number = data["phone_number"]

        customer_telegram_id = message.from_user.id
        update_customer_data(customer_telegram_id=customer_telegram_id, real_name=real_name, phone_number=phone_number)

        caption = f"Ваши данные сохранены, можно перейти к оформлению заказа!"
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=caption,
            reply_markup=BackToCart
        )
        await state.clear()

    async def select_address(self, callback: CallbackQuery):
        data = callback.data.split('_')
        address_id = data[-1]
        customer_telegram_id = callback.from_user.id

        customer = get_customer_by_telegram_id(customer_telegram_id)
        shopping_cart_items = get_customer_shopping_cart(customer_telegram_id)
        address = get_address_by_id(address_id=address_id)

        caption, keyboard = create_order_confirmation(shopping_cart_items, address, customer)

        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def change_recipient(self, callback: CallbackQuery):
        data = callback.data.split('_')
        address_id = data[-1]
        customer_telegram_id = callback.from_user.id

        address = get_address_by_id(address_id=address_id)
        customer = get_customer_by_telegram_id(customer_telegram_id)

        caption = (f"\n\nТекущий получатель: {address.recipient_name if address.recipient_name else customer.first_name}, Телефон: "
                f"{address.recipient_number if address.recipient_name else customer.phone}\n\n")

        if not address.recipient_name or not address.recipient_number:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Изменить получателя", callback_data=f"new_recipient_{address_id}")],
                [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address.address_id}")]
            ])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Получать заказ буду я", callback_data=f"set_recipient_customer_{address_id}")],
                [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address.address_id}")]
            ])

        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def new_recipient(self, callback: CallbackQuery, state: FSMContext):
        data = callback.data.split('_')
        address_id = data[-1]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address_id}")]
        ])
        caption = "Пожалуйста введите полное имя получателя\n(например: 'Владислав')"
        message = await callback.message.edit_caption(caption=caption, reply_markup=keyboard)
        await state.update_data(address_id=address_id)
        await state.update_data(message_id=message.message_id)
        await state.set_state(RecipientStates.FirstName)

    async def process_recipient_name(self, message: Message, state: FSMContext):
        await state.update_data(first_name=message.text)
        await message.delete()

        data = await state.get_data()
        address_id = data["address_id"]
        message_id = data.get("message_id")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address_id}")]
        ])

        caption = "Введите номер телефона получателя в любом формате:"
        await message.bot.edit_message_caption(chat_id=message.chat.id, message_id=message_id, caption=caption, reply_markup=keyboard)
        await state.set_state(RecipientStates.PhoneNumber)

    async def process_recipient_phone(self, message: Message, state: FSMContext):
        await state.update_data(phone_number=message.text)
        await message.delete()

        data = await state.get_data()
        address_id = data["address_id"]
        message_id = data["message_id"]
        real_name = data["first_name"]
        phone_number = data["phone_number"]

        change_recipient_in_address(address_id, real_name, phone_number)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address_id}")]
        ])

        caption = f"Ваши данные сохранены, можно перейти к оформлению заказа!"
        await message.bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=message_id,
            caption=caption,
            reply_markup=keyboard
        )
        await state.clear()

    async def set_recipient_customer(self, callback: CallbackQuery):
        data = callback.data.split('_')
        address_id = data[-1]

        change_recipient_in_address(address_id, None, None)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад к оформлению", callback_data=f"select_address_{address_id}")]
        ])

        await callback.message.edit_caption(caption='Получатель успешно изменен!', reply_markup=keyboard)

    async def proceed_to_payment(self, callback: CallbackQuery):
        data = callback.data.split('_')
        address_id = data[-1]
        caption = 'Подтвердите оплату заказа'
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_order_{address_id}")],
            [InlineKeyboardButton(text="Отменить", callback_data="shopping_cart")]
        ])

        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    async def confirm_order(self, callback: CallbackQuery):
        data = callback.data.split('_')
        address_id = data[-1]
        _, path = main_menu_text()
        customer_telegram_id = callback.from_user.id

        create_order_and_clear_cart(customer_telegram_id, address_id)

        caption = (f"Заказ успешно создан! Его статус вы можете отследить в личном кабинете"
                   f"\n\nТакже с вами может связаться наш менеджер для уточнения деталей")

        await callback.message.edit_caption(caption=caption, reply_markup=BackToMenu)


MainMenuCallbackHandler = MainMenuCallback(router_callback)
PersonalAccountCallbackHandler = PersonalAccountCallback(router_callback)
SupportCallbackHandler = SupportCallback(router_callback, get_admin_id())
CatalogCallbackHandler = CatalogCallback(router_callback)
ShoppingCartAndOrdersCallbackHandler = ShoppingCartAndOrdersCallback(router_callback)
PlaceOrderCallbackHandler = PlaceOrderCallback(router_callback)