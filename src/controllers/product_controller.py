from flask import request

from src.models.interfaces.product_repository_interface import ProductRepositoryInterface

class ProductController:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.__product_repository = product_repository

    def create_product(self, request):
        response = request.json

        if not response or "name" not in response or "price" not in response:
            raise Exception("Dados inválidos. Verifique as informações enviadas")

        name = response.get("name")
        price = response.get("price")

        if not name or not price:
            raise Exception("Dados inválidos, o nome e o valor do produto são obrigatórios")

        exists = self.__product_repository.get_product_by_name(name)

        if exists:
            raise Exception("Produto já existe")

        self.__product_repository.create_product(name=name, price=price)

    def get_products(self):
        products = self.__product_repository.get_products()

        return [p.to_dict() for p in products]

    def get_product_by_id(self, product_id: int):
        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise Exception("Produto não encontrado")

        return product.to_dict()

    def update_product(self, request, product_id: int):
        response = request.json

        if not response:
            raise Exception("Dados inválidos, verifique as informações enviadas")

        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise Exception("Produto não encontrado")

        fields = ["name", "price"]

        values_to_apply = {}
        for field in fields:
            if field in response:
                if not response[field]:
                    raise Exception("Dados inválidos. Tem certeza que enviou nome ou preço do produto?")

                values_to_apply[field] = response[field]

        if not values_to_apply:
            raise Exception("Nenhum campo válido enviado")

        self.__product_repository.update_product(product_id, values_to_apply)

    def delete_product(self, product_id: int):
        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise Exception("Produto não encontrado")

        self.__product_repository.delete_product(product_id)