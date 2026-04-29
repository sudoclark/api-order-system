from flask_login import UserMixin

from database import db
from OrderStatus import OrderStatus

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(80), nullable=False, default="user")

    # Relacionamentos -- O usuário tem um pedido
    orders = db.relationship("Order", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)

    # Relacionamento -- O produto vira um OrderItem quando adicionado a um Order. Imaginemos que um restaurante tem um cardápio -> esses são os produtos.
    # Dentro do cardápio o usuário escolhe um desses produtos para comprar e o adiciona na sacola -> vira um OrderItem.
    order_items = db.relationship("OrderItem", backref="product", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }
    

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relacionamento -- Um OrderItem está relacionado a um Order -> um OrderItem faz parte de um pedido.
    # Carrega o product.id para sabermos a qual produto ele se refere.
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

    # Com o valor e a quantidade, calculamos o toal DESSE PRODUTO no pedido
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


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(40), nullable=False, default=OrderStatus.PENDING)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) # Relacionamento com a tabela User

    # Um pedido tem vários OrderItems
    order_items = db.relationship("OrderItem", backref="order", lazy=True)
    

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "user_id": self.user_id,
            "customer_name": self.user.name, # Esse user vem do relacionamento com a tabela User. Isso está definido lá na tabela User (parte lógica do relacionamento)
            "items": [item.to_dict() for item in self.order_items],
            "total": sum(item.get_total() for item in self.order_items)
        }