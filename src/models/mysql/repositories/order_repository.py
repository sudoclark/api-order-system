from src.models.mysql.settings.connect import DbManager
from src.models.mysql.entities.order import OrderItem, Order

class OrderRepository:
    def __init__(self, db_connection: DbManager):
        self.__db_connection = db_connection

    # =======================
    # ORDER_ITEM
    # =======================

    def add_item(self, quantity: int, order_id: int, product_id: int):
        try:
            with self.__db_connection as db:
                order_item = OrderItem(quantity=quantity, order_id=order_id, product_id=product_id)

                db.session.add(order_item)
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def update_order_item(self, order_item_id: int, quantity: int):
        try:
            with self.__db_connection as db:
                order_item = db.session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
                order_item.quantity = quantity

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def get_order_iten_by_id(self, order_item_id: int):
        with self.__db_connection as db:
            order_item = db.session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
            return order_item

    def delete_order_item(self, order_item_id: int):
        try:
            with self.__db_connection as db:
                db.session.query(OrderItem).filter(OrderItem.id == order_item_id).delete()
                
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    # =======================
    # ORDER
    # =======================

    def create_order(self, user_id: int):
        try:
            with self.__db_connection as db:
                order = Order(user_id=user_id)

                db.session.add(order)
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def get_orders(self):
        with self.__db_connection as db:
            orders = db.session.query(Order).all()
            return orders

    def get_order_by_id(self, order_id: int):
        with self.__db_connection as db:
            order = db.session.query(Order).filter(Order.id == order_id).first()
            return order

    def get_orders_from_user_by_id(self, user_id: int):
        with self.__db_connection as db:
            orders = db.session.query(Order).filter(Order.user_id == user_id).all()
            return orders

    def get_ordersItens_from_specif_order(self, order_id: int):
        with self.__db_connection as db:
            order = db.session.query(Order).filter(Order.id == order_id).first()
            order_itens = order.order_items

            return order_itens

    def get_order_by_status_and_user_id(self, status: str, user_id: int):
        with self.__db_connection as db:
            order = db.session.query(Order).filter(Order.status == status, Order.user_id == user_id).first()
            return order

    def update_order_status(self, order_id: int, new_status: str):
        try:
            with self.__db_connection as db:
                order = db.session.query(Order).filter(Order.id == order_id).first()
                order.status = new_status

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def delete_order(self, order_id: int):
        try:
            with self.__db_connection as db:
                db.session.query(Order).filter(Order.id == order_id).delete()

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex