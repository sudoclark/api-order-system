from flask import request
from flask_login import current_user

from OrderStatus import OrderStatus
from src.models.mysql.repositories.order_repository import OrderRepository
from src.models.mysql.repositories.product_repository import ProductRepository

class OrderController:
    def __init__(self, order_repository: OrderRepository, product_repository: ProductRepository):
        self.__order_repository = order_repository
        self.__product_repository = product_repository
        

    # ===============================
    # ORDER_ITEM CONTROLLER
    # ===============================

    def add_item(self, request):
        response = request.json

        if not response:
            raise Exception("Dados inválidos. Verifique as informações enviadas!")

        quantity = response.get("quantity")
        product_name = response.get("product_name")

        if not quantity or not product_name:
            raise Exception("Dados inválidos, a quantidade e o nome do produto são obrigatórios!")

        if not isinstance(quantity, int):
            raise Exception("A quantidade precisa ser um número inteiro")

        order = self.__order_repository.get_order_by_status_and_user_id("PENDENTE", current_user.id)

        if not order:
            raise Exception("Pedido não encontrado. Certifique-se que esse usuário já possui um pedido em aberto no sistema")

        product = self.__product_repository.get_product_by_name(product_name)

        if not product:
            raise Exception("Produto não encontrado, verifique as informações enviadas")

        self.__order_repository.add_item(quantity=quantity, order_id=order.id, product_id=product.id)

    def update_order_item(self, request, order_iten_id: int):
        response = request.json

        if not response:
            raise Exception("Dados inválidos. Verifique as informações enviadas")

        quantity = response.get("quantity")

        if not quantity:
            raise Exception("A quantidade é obrigatória")

        order_item = self.__order_repository.get_order_iten_by_id(order_iten_id)

        if not order_item:
            raise Exception("Produto não encontrado")

        if order_item.order.user_id != current_user.id:
            raise Exception("Você não pode alterar o pedido de outra pessoa")

        if not isinstance(quantity, int):
            raise Exception("A quantidade precisa ser um número inteiro")

        self.__order_repository.update_order_item(order_item_id=order_iten_id, quantity=response["quantity"])

    def delete_order_item(self, order_item_id: int):
        order_item = self.__order_repository.get_order_iten_by_id(order_item_id)

        if not order_item:
            raise Exception("Produto não encontrado")

        if order_item.order.user_id != current_user.id:
            raise Exception("Você não tem permissão para deletar o pedido de outra pessoa")

        self.__order_repository.delete_order_item(order_item_id)


    # ===============================
    # ORDER CONTROLLER
    # ===============================

    def create_order(self):
        self.__order_repository.create_order(current_user.id)

    def get_orders(self):
        orders = self.__order_repository.get_orders()

        return [order.to_dict() for order in orders]

    def get_order_by_id(self, order_id: int):
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise Exception("Pedido não encontrado")

        if current_user.role != "admin" and current_user.id != order.user_id:
            raise Exception("Você não tem permissão para visualizar um pedido de outro usuário. Verifique com um admin")

        return order.to_dict()

    def get_orders_from_specif_user(self):
        orders = self.__order_repository.get_orders_from_user_by_id(current_user.id)

        return [order.to_dict() for order in orders]

    def get_orderItems_from_specific_order(self, order_id: int):
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise Exception("Pedido não encontrado")

        if current_user.id != order.user_id:
            raise Exception("Você não pode visualizar itens dos pedidos de outros usuários")

        order_items = order.order_items

        return [oi.to_dict() for oi in order_items]

    def update_order_status(self, action, order_id: int):
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise Exception("Pedido não encontrado")

        if action == "cancel":
            if order.status != "PENDENTE":
                raise Exception("Esse pedido não pode ser cancelado")

            self.__order_repository.update_order_status(order_id=order_id, new_status=OrderStatus.CANCELLED)

        elif action == "pay":
            if order.status != "PENDENTE":
                raise Exception("Esse pedido não pode ser pago")

            self.__order_repository.update_order_status(order_id=order_id, new_status=OrderStatus.PAID)

        else:
            raise Exception("Opção inválida")


    def delete_order(self, order_id: int):
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise Exception("Pedido não encontrado")

        self.__order_repository.delete_order(order_id=order_id)