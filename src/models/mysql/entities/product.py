from sqlalchemy import Column, INTEGER, String, REAL
from sqlalchemy.orm import relationship, validates

from src.models.mysql.settings.base import Base

class Product(Base):
    __tablename__ = "product"

    id = Column(INTEGER, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(REAL, nullable=False)

    order_items = relationship("OrderItem", backref="product", lazy=True)

    @validates('price')
    def validate_price(self, _key, value):
        if not isinstance(value, (int, float)):
            raise ValueError("O valor precisa ser um número!")
        if value <= 0:
            raise ValueError("O valor precisa ser um número positivo maior que zero!")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }
