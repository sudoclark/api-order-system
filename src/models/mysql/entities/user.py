from flask_login import UserMixin
from sqlalchemy import Column, INTEGER, String, LargeBinary
from sqlalchemy.orm import relationship, validates

from src.models.mysql.settings.base import Base

class User(Base, UserMixin):
    __tablename__ = "user"

    id = Column(INTEGER, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    role = Column(String(30), nullable=False, default="user")

    orders = relationship("Order", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
