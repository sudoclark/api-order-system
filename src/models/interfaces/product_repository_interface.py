from abc import ABC, abstractmethod

class ProductRepositoryInterface():
    @abstractmethod
    def create_product(self, name: str, price: float) -> None: pass

    @abstractmethod
    def get_products(self) -> list: pass

    @abstractmethod
    def get_product_by_id(self, product_id: int): pass

    @abstractmethod
    def get_product_by_name(self, name: str): pass

    @abstractmethod
    def update_product(self, product_id: int, fields: dict) -> None: pass

    @abstractmethod
    def delete_product(self, product_id: int) -> None: pass