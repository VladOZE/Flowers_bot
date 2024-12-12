from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.filters import Command
from aiogram import Router, F
from functions import *
from keyboards import *
from quaries import *
from states import SupportStates, PersonalOrderStates
from aiogram.fsm.context import FSMContext
import time


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
    #    self.router.callback_query(F.data.startswith("view_ticket_"))(self.view_ticket)
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
            [InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")]
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
            [InlineKeyboardButton(text="Назад в личный кабинет", callback_data="personal_account")]
        )

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        photo = InputMediaPhoto(media=FSInputFile(path), caption=caption)
        await callback.message.edit_media(media=photo, reply_markup=reply_markup)

    # async def view_ticket(self, callback: CallbackQuery):

    # async def feedback_form(self, callback: CallbackQuery):


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

        await callback.message.edit_media(media=photo, reply_markup=create_cart_item_keyboard(product_id))

    async def change_quantity(self, callback: CallbackQuery):
        product_id = int(callback.data.split('_')[-1])
        product = get_product_by_id(product_id)
        if not product:
            await callback.answer("Информация о товаре недоступна.")
            return
        caption = (f'Товар: {product.name}, текущее кол-во: {product.count}'
                   'Выберите насколько хотите изменить кол-во:')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="+1", callback_data=f"increase_quantity_{product_id}_1"),
                InlineKeyboardButton(text="+2", callback_data=f"increase_quantity_{product_id}_2"),
                InlineKeyboardButton(text="+5", callback_data=f"increase_quantity_{product_id}_5"),
            ],
            [
                InlineKeyboardButton(text="-1", callback_data=f"decrease_quantity_{product_id}_1"),
                InlineKeyboardButton(text="-2", callback_data=f"decrease_quantity_{product_id}_2"),
                InlineKeyboardButton(text="-5", callback_data=f"decrease_quantity_{product_id}_5"),
            ],
            [InlineKeyboardButton(text="Назад к товару", callback_data=f"cart_item_{product_id}")],
        ]
    )




MainMenuCallbackHandler = MainMenuCallback(router_callback)
PersonalAccountCallbackHandler = PersonalAccountCallback(router_callback)
SupportCallbackHandler = SupportCallback(router_callback, get_admin_id())
CatalogCallbackHandler = CatalogCallback(router_callback)
ShoppingCartAndOrdersCallbackHandler = ShoppingCartAndOrdersCallback(router_callback)
