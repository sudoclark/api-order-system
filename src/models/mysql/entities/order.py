from sqlalchemy import Column, INTEGER, String, ForeignKey
from sqlalchemy.orm import relationship

from src.models.mysql.settings.base import Base

class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(INTEGER, primary_key=True)
    quantity = Column(INTEGER, nullable=False, default=1)

    order_id = Column(INTEGER, ForeignKey("order.id"), nullable=False)
    product_id = Column(INTEGER, ForeignKey("product.id"), nullable=False)

    def get_total(self):
        return self.quantity * self.product.price

    def to_dict(self):
        return {
            "id": self.id,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "product_id": self.product_id, # Esse product vem do relacionamento com a tabela Product. Isso está definido na tabela Product (parte lógica do relacionamento)
            "product_name": self.product.name,
            "product_price": self.product.price,
            "subtotal": self.get_total()
        }

class Order(Base):
    __tablename__ = "order"

    id = Column(INTEGER, primary_key=True)
    status = Column(String(100), nullable=False, default="pending")
    user_id = Column(INTEGER, ForeignKey("user.id"), nullable=False)

    order_items = relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "user_id": self.user_id,
            "customer_name": self.user.username, # Esse user vem do relacionamento com a tabela User. Isso está definido lá na tabela User (parte lógica do relacionamento)
            "items": [item.to_dict() for item in self.order_items],
            "total": sum(item.get_total() for item in self.order_items)
        }
