from src.database.database_base import Session
from src.database.models import *


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
