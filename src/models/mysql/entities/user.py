from flask_login import UserMixin
from sqlalchemy import Column, INTEGER, String, LargeBinary
from sqlalchemy.orm import relationship, backref, validates

from src.models.mysql.settings.base import Base

class User(Base, UserMixin):
    __tablename__ = "user"

    id = Column(INTEGER, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    role = Column(String(30), nullable=False, default="user")
    """
    Originalmente essa linha era assim: orders = relationship("Order", backref="user", lazy=True).
    Isso criava um caminho único: só busque o user.orders quando eu explicitamente dizer para buscar,
    ou seja, quando eu chamar user.orders.
    Isso criava um grande problema com a sessão do db, pois ele buscava o usuário e fechava a sessão,
    então quando eu tentava buscar o orders, a sessão já tinha expirado e dava erro.

    Com essa nova implementação ele faz os dois caminhos: quando busca o User, já busca o orders; quando
    busca o Order, já busca os users. Além disso o lazy="joined" faz isso em uma query só, ou seja, na
    mesma sessão.
    """
    orders = relationship("Order", backref=backref("user", lazy="joined"), lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
