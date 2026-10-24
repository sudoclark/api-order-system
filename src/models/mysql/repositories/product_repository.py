from src.models.mysql.settings.connect import DbManager
from src.models.mysql.entities.product import Product

class ProductRepository:
    def __init__(self, db_connection: DbManager):
        self.__db_connection = db_connection

    def create_product(self, name: str, price: float) -> None:
        try:
            with self.__db_connection as db:
                product = Product(name=name, price=price)

                db.session.add(product)
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def get_products(self) -> list:
        with self.__db_connection as db:
            products = db.session.query(Product).all()
            return products

    def get_product_by_id(self, id: int) -> Product:
        with self.__db_connection as db:
            product = db.session.query(Product).filter(Product.id == id).first()
            return product

    def get_product_by_name(self, name: str):
        with self.__db_connection as db:
            product = db.session.query(Product).filter(Product.name == name).first()
            return product

    def update_product(self, id: int, fields: dict) -> None:
        try:
            with self.__db_connection as db:
                product = db.session.query(Product).filter(Product.id == id).first()
                
                for field, value in fields.items():
                    setattr(product, field, value)

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def delete_product(self, id: int) -> None:
        try:
            with self.__db_connection as db:
                db.session.query(Product).filter(Product.id == id).delete()

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

