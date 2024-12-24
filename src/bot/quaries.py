from src.database.database_base import Session
from src.database.models import *
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from typing import List
from datetime import datetime


def get_customer(customer_telegram_id: int) -> Customer:
    with Session() as session:
        customer = session.query(Customer).filter(Customer.customer_telegram_id == customer_telegram_id).first()
        session.close()
        return customer


def customer_in_db(customer_telegram_id: int) -> bool:
    if get_customer(customer_telegram_id):
        return True
    return False


def add_customer(customer_telegram_id: int, first_name: str) -> None:
    if not customer_in_db(customer_telegram_id):
        new_customer = Customer(customer_telegram_id=customer_telegram_id,
                                first_name=first_name, amount_orders=0)
        with Session() as session:
            session.add(new_customer)
            session.commit()
            session.close()


def get_customer_mailing(customer_telegram_id: int) -> int:
    with Session() as session:
        mailing_status = session.query(Customer.mailing).filter(Customer.customer_telegram_id == customer_telegram_id).first()
        session.close()
        return mailing_status


def get_customer_tickets(customer_telegram_id: int) -> List[SupportTicket]:
    with Session() as session:
        customer_tickets = session.query(SupportTicket).filter(Customer.customer_telegram_id == customer_telegram_id).all()
        session.close()
        print(customer_tickets)
        return customer_tickets


def create_ticket(customer_telegram_id: int) -> SupportTicket:
    with Session() as session:
        ticket = SupportTicket(customer_telegram_id=customer_telegram_id)
        session.add(ticket)
        session.commit()

        ticket = session.query(SupportTicket).filter_by(ticket_id=ticket.ticket_id).first()
        session.close()

    return ticket


def add_message_to_ticket(message_id: int, ticket_id: int, sender_type: str, text: str) -> SupportMessage:
    message = SupportMessage(message_id=message_id, ticket_id=ticket_id, sender_type=sender_type, message_text=text)
    with Session() as session:
        session.add(message)
        session.commit()
        session.close()
    return message


def get_ticket_by_id(ticket_id: int) -> SupportTicket | None:
    with Session() as session:
        ticket = session.query(SupportTicket).options(joinedload(SupportTicket.messages)).filter(SupportTicket.ticket_id == ticket_id).first()
        session.close()
    return ticket


def set_ticket_status_open(ticket_id: int) -> None:
    with Session() as session:
        ticket = session.query(SupportTicket).filter_by(ticket_id=ticket_id).first()
        if ticket:
            ticket.status = 'open'
            session.commit()
            session.close()


def set_ticket_status_closed(ticket_id: int) -> None:
    with Session() as session:
        ticket = session.query(SupportTicket).filter_by(ticket_id=ticket_id).first()
        if ticket:
            ticket.status = 'closed'
            session.commit()
            session.close()


def get_customer_tickets(customer_id: int, status: str) -> List[SupportTicket]:
    with Session() as session:
        tickets = (
            session.query(SupportTicket)
            .filter_by(customer_telegram_id=customer_id, status=status.lower())
            .order_by(SupportTicket.ticket_id.asc())
            .all()
        )
    session.close()
    return tickets


def get_ticket_messages(ticket_id: int):
    with Session() as session:
        messages = session.query(SupportMessage).filter_by(ticket_id=ticket_id).all()
        session.close()
    return messages



def get_flowers_list() -> List[Product]:
    with Session() as session:
        flowers = (
            session.query(Product)
            .filter_by(product_type='flower')
            .order_by(Product.product_id.asc())
            .all()
        )
    session.close()
    return flowers


def get_products_list(product_type: str) -> List[Product]:
    with Session() as session:
        products = (
            session.query(Product)
            .filter_by(product_type=product_type)
            .order_by(Product.product_id.asc())
            .all()
        )
    session.close()
    return products


def get_product_by_id(product_id: int) -> dict:
    with Session() as session:
        product = (
            session.query(Product)
            .filter_by(product_id=product_id).first()
        )
    session.close()
    return product


def create_personal_order(telegram_id: int, description: str, photo_path: str, status: str) -> PersonalOrder:
    with Session() as session:
        personal_order = PersonalOrder(
            customer_telegram_id=telegram_id,
            description=description,
            image=photo_path,
            status=status
        )
        session.add(personal_order)
        session.commit()
        session.refresh(personal_order)
    session.close()
    return personal_order


def update_personal_order(personal_order_id: int, description: str, photo_path: str, status: str) -> PersonalOrder:
    with Session() as session:
        personal_order = session.query(PersonalOrder).filter(PersonalOrder.personal_order_id == personal_order_id).first()

        if not personal_order:
            return None

        personal_order.description = description
        personal_order.image = photo_path
        personal_order.status = status

        session.commit()

        session.refresh(personal_order)

    session.close()
    return personal_order


def get_personal_order_by_id(order_id: int) -> PersonalOrder:
    with Session() as session:
        return session.query(PersonalOrder).filter(PersonalOrder.personal_order_id == order_id).first()


def set_personal_order_status_closed(order_id: int) -> None:
    with Session() as session:
        personal_order = session.query(PersonalOrder).filter(PersonalOrder.personal_order_id == order_id).first()
        personal_order.status = 'closed'
        session.commit()
        session.close()
    return


def add_to_shopping_cart(customer_telegram_id: int, product_id: int, count: int = 1):
    new_cart = ShoppingCart(customer_telegram_id=customer_telegram_id, product_id=product_id, count=count)
    with Session() as session:
        session.add(new_cart)
        session.commit()
    session.close()
    return


def get_customer_shopping_cart(customer_telegram_id: int):
    with Session() as session:
        query = (
            select(ShoppingCart, Product)
            .join(Product, ShoppingCart.product_id == Product.product_id)
            .where(ShoppingCart.customer_telegram_id == customer_telegram_id)
        )
        results = session.execute(query).all()
    session.close()
    return results


def get_existing_cart_item(customer_telegram_id: int, product_id: int):
    with Session() as session:
        return session.query(ShoppingCart).filter_by(
            customer_telegram_id=customer_telegram_id,
            product_id=product_id
        ).first()


def update_cart_item_quantity(customer_telegram_id: int, product_id: int, delta: int) -> int:
    with Session() as session:
        cart_item = session.query(ShoppingCart).filter_by(
            customer_telegram_id=customer_telegram_id,
            product_id=product_id
        ).first()

        if not cart_item:
            raise ValueError("Товар не найден в корзине.")

        cart_item.count = max(1, cart_item.count + delta)
        session.commit()
        return cart_item.count


def remove_from_cart(customer_telegram_id: int, product_id: int):
    with Session() as session:
        cart_item = session.query(ShoppingCart).filter_by(
            customer_telegram_id=customer_telegram_id,
            product_id=product_id
        ).first()

        if not cart_item:
            raise ValueError("Товар не найден в корзине.")

        session.delete(cart_item)
        session.commit()


def get_customer_by_telegram_id(customer_telegram_id: int) -> Customer | None:
    with Session() as session:
        customer = session.query(Customer).filter_by(customer_telegram_id=customer_telegram_id).first()
        return customer if customer else None


def get_customer_addresses(customer_telegram_id: int) -> List[Addresses] | None:
    with Session() as session:
        customer = session.query(Customer).filter_by(customer_telegram_id=customer_telegram_id).first()
        if not customer:
            return None

        addresses = session.query(Addresses).filter_by(customer_id=customer.customer_id).all()
        return addresses if addresses else None


def add_new_address(address: Addresses) -> None:
    with Session() as session:
        session.add(address)
        session.commit()
    session.close()


def get_address_by_id(address_id: int) -> Addresses:
    with Session() as session:
        address = session.query(Addresses).filter_by(address_id=address_id).first()
        session.close()
    return address


def update_customer_data(customer_telegram_id: int, first_name: str = None, last_name: str = None,
                         real_name: str = None, phone_number: str = None, email: str = None) -> None:
    with Session() as session:
        customer = session.query(Customer).filter(Customer.customer_telegram_id == customer_telegram_id).first()

        print(f"Before update: {customer.__dict__}")
        if first_name is not None:
            customer.first_name = first_name
        if last_name is not None:
            customer.last_name = last_name
        if real_name is not None:
            customer.real_name = real_name
        if phone_number is not None:
            customer.phone = phone_number
        if email is not None:
            customer.email = email
        print(f"After update: {customer.__dict__}")

        session.commit()


def change_recipient_in_address(address_id, new_name: str, new_phone_number: str) -> Addresses:
    with Session() as session:
        address: Addresses = session.query(Addresses).filter(Addresses.address_id == address_id).first()
        address.recipient_name = new_name
        address.recipient_number = new_phone_number
        session.commit()
        session.refresh(address)
    session.close()
    return address


def create_order_and_clear_cart(customer_telegram_id: int, address_id: int) -> None:
    with Session() as session:
        customer = session.query(Customer).filter_by(customer_telegram_id=customer_telegram_id).first()

        query = (
            select(ShoppingCart, Product)
            .join(Product, ShoppingCart.product_id == Product.product_id)
            .where(ShoppingCart.customer_telegram_id == customer_telegram_id)
        )
        cart_items = session.execute(query).all()

        new_order = Order(
            customer_id=customer.customer_id,
            order_date=datetime.now(),
            total_price=sum(product.price * shopping_cart.count for shopping_cart, product in cart_items),
            status='pending',
            address_id=address_id
        )

        session.add(new_order)
        session.commit()
        session.refresh(new_order)


        for shopping_cart, product in cart_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=product.product_id,
                quantity=shopping_cart.count,
                price=product.price,
            )
            session.add(order_item)

        session.query(ShoppingCart).filter_by(customer_telegram_id=customer_telegram_id).delete()

        session.commit()


def get_user_orders(customer_telegram_id: int):
    with Session() as session:
        orders = (
            session.query(Order)
            .join(Customer, Order.customer_id == Customer.customer_id)
            .filter(Customer.customer_telegram_id == customer_telegram_id)
            .order_by(Order.order_date.asc()).all()
        )
        session.close()
    return orders


def get_order_by_id(order_id: int) -> Order:
    with Session() as session:
        query = (
            select(Order)
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.product)
            )
            .where(Order.order_id == order_id)
        )
        result = session.execute(query).scalars().first()
    return result

