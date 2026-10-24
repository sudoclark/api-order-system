from abc import ABC, abstractmethod

class OrderRepositoryInterface():
    @abstractmethod
    def add_item(self, quantity: int, order_id: int, product_id: int): pass

    @abstractmethod
    def update_order_item(self, order_item_id: int, quantity: int): pass

    @abstractmethod
    def get_order_iten_by_id(self, order_item_id: int): pass

    @abstractmethod
    def delete_order_item(self, order_item_id: int): pass


    @abstractmethod
    def create_order(self, user_id: int): pass

    @abstractmethod
    def get_orders(self): pass

    @abstractmethod
    def get_order_by_id(self, order_id: int): pass

    @abstractmethod
    def get_orders_from_user_by_id(self, user_id: int): pass

    @abstractmethod
    def get_ordersItens_from_specif_order(self, order_id: int): pass

    @abstractmethod
    def get_order_by_status_and_user_id(self, status: str, user_id: int): pass

    @abstractmethod
    def update_order_status(self, order_id: int, new_status: str): pass

    @abstractmethod
    def delete_order(self, order_id: int): pass