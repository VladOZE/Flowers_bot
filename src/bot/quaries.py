from src.database.database_base import Session
from src.database.models import *
from sqlalchemy.orm import joinedload
from typing import List


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


def get_customer_tickets(customer_id: int, status: str) -> list[SupportTicket]:
    with Session() as session:
        tickets = (
            session.query(SupportTicket)
            .filter_by(customer_telegram_id=customer_id, status=status.lower())
            .order_by(SupportTicket.ticket_id.asc())
            .all()
        )
    session.close()
    return tickets
