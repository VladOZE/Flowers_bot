from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DECIMAL, TIMESTAMP, DATE, func
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, BIGINT
from sqlalchemy.orm import relationship
import enum
from src.database.database_base import Base


class ProductTypeEnum(enum.Enum):
    flower = "flower"
    bouquet = "bouquet"
    toy = "toy"


class PaymentMethodEnum(enum.Enum):
    card = "card"
    cash = "cash"
    online = "online"


class PaymentStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class DeliveryStatusEnum(enum.Enum):
    pending = "scheduled"
    shipped = "in transit"
    delivered = "delivered"
    cancelled = "failed"


class OrderStatusEnum(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class SupportSenderType(enum.Enum):
    user = "user"
    admin = "admin"


class SupportStatus(enum.Enum):
    open = "open"
    closed = "closed"


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    product_type = Column(Enum(ProductTypeEnum), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), default=None)
    in_stock = Column(Integer, default=None)
    description = Column(Text, default=None)
    image_url = Column(String(255), default=None)

    order_items = relationship("OrderItem", back_populates="product")


class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    customer_telegram_id = Column(BIGINT(unsigned=True), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), default=None)
    patronymic = Column(String(100), default=None)
    email = Column(String(100), default=None)
    phone = Column(String(15), default=None)
    amount_orders = Column(INTEGER(unsigned=True), nullable=False, default=0)
    mailing = Column(TINYINT(unsigned=True), default=1)


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    customer_id = Column(INTEGER(unsigned=True), ForeignKey('customers.customer_id'), nullable=False)
    order_date = Column(TIMESTAMP, nullable=False)
    total_price = Column(DECIMAL(10, 2), default=None)
    status = Column(Enum(OrderStatusEnum), nullable=False)

    customer = relationship("Customer", backref="orders")
    order_items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", back_populates="order")
    delivery = relationship("Delivery", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_id = Column(INTEGER(unsigned=True), ForeignKey('orders.order_id'), primary_key=True, nullable=False)
    product_id = Column(INTEGER(unsigned=True), ForeignKey('products.product_id'), primary_key=True, nullable=False)
    product_type = Column(Enum(ProductTypeEnum), nullable=False)
    quantity = Column(INTEGER(unsigned=True), nullable=False)
    price = Column(DECIMAL(10, 2), default=None)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class BouquetFlower(Base):
    __tablename__ = 'bouquet_flowers'

    bouquet_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    flower_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    quantity = Column(INTEGER(unsigned=True), default=None)


class Payment(Base):
    __tablename__ = 'payment'

    payment_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    order_id = Column(INTEGER(unsigned=True), ForeignKey('orders.order_id'), nullable=False)
    payment_date = Column(TIMESTAMP, nullable=False)
    amount = Column(DECIMAL(10, 2), default=None)
    method = Column(Enum(PaymentMethodEnum), default=None)
    status = Column(Enum(PaymentStatusEnum), nullable=False)

    order = relationship("Order", back_populates="payment")


class Delivery(Base):
    __tablename__ = 'delivery'

    delivery_id = Column(INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    order_id = Column(INTEGER(unsigned=True), ForeignKey('orders.order_id'), nullable=False)
    delivery_date = Column(DATE, default=None)
    delivery_status = Column(Enum(DeliveryStatusEnum), nullable=False)
    courier_name = Column(String(100), default=None)
    tracking_number = Column(String(100), default=None)

    order = relationship("Order", back_populates="delivery")


class SupportTicket(Base):
    __tablename__ = 'support_tickets'

    ticket_id = Column(BIGINT(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    customer_telegram_id = Column(BIGINT(unsigned=True), nullable=False)
    status = Column(Enum(SupportStatus), nullable=False, default='open')
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)

    messages = relationship("SupportMessage", back_populates="ticket")


class SupportMessage(Base):
    __tablename__ = 'support_messages'

    message_id = Column(BIGINT(unsigned=True), primary_key=True, nullable=False, autoincrement=True)
    ticket_id = Column(BIGINT(unsigned=True), ForeignKey('support_tickets.ticket_id'), nullable=False)
    sender_type = Column(Enum(SupportSenderType), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)

    ticket = relationship("SupportTicket", back_populates="messages")