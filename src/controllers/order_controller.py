from flask_login import current_user

from src.schemas.order_status import OrderStatus
from src.errors.http_errors.not_found_error import NotFoundError
from src.errors.http_errors.forbidden_error import ForbiddenError
from src.errors.http_errors.bad_request_error import BadRequestError
from src.models.interfaces.order_repository_interface import OrderRepositoryInterface
from src.errors.http_errors.unprocessable_entity_error import UnprocessableEntityError
from src.models.interfaces.product_repository_interface import ProductRepositoryInterface

class OrderController:
    def __init__(self, order_repository: OrderRepositoryInterface, product_repository: ProductRepositoryInterface):
        self.__order_repository = order_repository
        self.__product_repository = product_repository
        

    # ===============================
    # ORDER_ITEM CONTROLLER
    # ===============================

    def add_item(self, request):
        """
        Adiciona um produto a um pedido em aberto (status 'PENDENTE') do usuário autenticado.
        Verifica se os campos 'quantity' e 'product_name' estão presentes na requisição e não estão vazios.
        A quantidade deve ser um número inteiro e o produto deve existir no sistema.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Pedido não encontrado. Certifique-se que esse usuário já possui um pedido em aberto no sistema"}
                         {"status": "OK", "message": "Produto adicionado ao pedido"}
        """
        response = request.json

        if not response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas!")

        quantity = response.get("quantity")
        product_name = response.get("product_name")

        if not quantity or not product_name:
            raise BadRequestError("Dados inválidos, a quantidade e o nome do produto são obrigatórios!")

        if not isinstance(quantity, int):
            raise UnprocessableEntityError("A quantidade precisa ser um número inteiro")

        order = self.__order_repository.get_order_by_status_and_user_id("PENDENTE", current_user.id)

        if not order:
            raise NotFoundError("Pedido não encontrado. Certifique-se que esse usuário já possui um pedido em aberto no sistema")

        product = self.__product_repository.get_product_by_name(product_name)

        if not product:
            raise NotFoundError("Produto não encontrado, verifique as informações enviadas")

        self.__order_repository.add_item(quantity=quantity, order_id=order.id, product_id=product.id)

    def update_order_item(self, request, order_iten_id: int):
        """
        Atualiza a quantidade de um item em um pedido pelo ID do item.
        O usuário autenticado só pode alterar itens de seus próprios pedidos.
        O campo 'quantity' deve ser um número inteiro.

        Requer autenticação.

        Args:
            id (int): ID do item do pedido a ser atualizado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Você não pode alterar o pedido de outra pessoa."}
                         {"status": "OK", "message": "Quantidade alterada com sucesso."}
        """
        response = request.json

        if not response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

        quantity = response.get("quantity")

        if not quantity:
            raise BadRequestError("A quantidade é obrigatória")

        order_item = self.__order_repository.get_order_iten_by_id(order_iten_id)

        if not order_item:
            raise NotFoundError("Produto não encontrado")

        if order_item.order.user_id != current_user.id:
            raise ForbiddenError("Você não pode alterar o pedido de outra pessoa")

        if not isinstance(quantity, int):
            raise UnprocessableEntityError("A quantidade precisa ser um número inteiro")

        self.__order_repository.update_order_item(order_item_id=order_iten_id, quantity=response["quantity"])

    def delete_order_item(self, order_item_id: int):
        """
        Remove um item de um pedido pelo seu ID.
        O usuário autenticado só pode remover itens de seus próprios pedidos.

        Requer autenticação.

        Args:
            id (int): ID do item do pedido a ser removido.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Você não pode deletar o pedido de outra pessoa."}
                         {"status": "OK", "message": "Produto deletado com sucesso."}
        """
        order_item = self.__order_repository.get_order_iten_by_id(order_item_id)

        if not order_item:
            raise NotFoundError("Produto não encontrado")

        if order_item.order.user_id != current_user.id:
            raise ForbiddenError("Você não tem permissão para deletar o pedido de outra pessoa")

        self.__order_repository.delete_order_item(order_item_id)


    # ===============================
    # ORDER CONTROLLER
    # ===============================

    def create_order(self):
        """
        Cria um novo pedido para o usuário autenticado com status inicial 'PENDENTE'.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Pedido criado com sucesso."}
        """
        self.__order_repository.create_order(current_user.id)

    def get_orders(self):
        """
        Retorna a listagem de todos os pedidos cadastrados no sistema.
        Apenas administradores podem realizar essa operação.

        Requer autenticação e cargo 'admin'.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "orders": [...]}
        """
        orders = self.__order_repository.get_orders()

        return [order.to_dict() for order in orders]

    def get_order_by_id(self, order_id: int):
        """
        Retorna as informações de um pedido específico pelo seu ID.
        Usuários com cargo 'user' só podem consultar seus próprios pedidos.
        Usuários com cargo 'admin' podem consultar qualquer pedido.

        Requer autenticação.

        Args:
            id (int): ID do pedido a ser consultado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                         {"status": "OK", "message": "Pedido obtido com sucesso.", "order": {...}}
        """
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise NotFoundError("Pedido não encontrado")

        if current_user.role != "admin" and current_user.id != order.user_id:
            raise ForbiddenError("Você não tem permissão para visualizar um pedido de outro usuário. Verifique com um admin")

        return order.to_dict()

    def get_orders_from_specif_user(self):
        """
        Retorna a listagem de todos os pedidos do usuário autenticado.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "orders": [...]}
        """
        orders = self.__order_repository.get_orders_from_user_by_id(current_user.id)

        return [order.to_dict() for order in orders]

    def get_orderItems_from_specific_order(self, order_id: int):
        """
        Retorna a listagem de todos os itens de um pedido específico pelo ID do pedido.
        Usuários com cargo 'user' só podem consultar itens de seus próprios pedidos.

        Requer autenticação.

        Args:
            id (int): ID do pedido cujos itens serão listados.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                         {"status": "ERROR", "message": "Você não pode visualizar itens dos pedidos de outros usuários."}
                         {"status": "OK", "message": "Listagem obtida com sucesso.", "order_items": [...]}
        """
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise NotFoundError("Pedido não encontrado")

        if current_user.id != order.user_id:
            raise ForbiddenError("Você não pode visualizar itens dos pedidos de outros usuários")

        order_items = order.order_items

        return [oi.to_dict() for oi in order_items]

    def update_order_status(self, action, order_id: int):
        """
        Atualiza o status de um pedido pelo seu ID com base na ação informada.
        As ações válidas são 'cancel' (cancela o pedido) e 'pay' (marca o pedido como pago).
        Ambas as ações só podem ser executadas em pedidos com status 'PENDENTE'.
        Apenas administradores podem realizar essa operação.

        Requer autenticação e cargo 'admin'.

        Args:
            action (str): Ação a ser realizada no pedido. Valores aceitos: 'cancel', 'pay'.
            id (int): ID do pedido a ser atualizado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                         {"status": "ERROR", "message": "Opção inválida."}
                         {"status": "OK", "message": "Pedido cancelado com sucesso."}
                         {"status": "OK", "message": "Pedido pago com sucesso."}
        """
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise NotFoundError("Pedido não encontrado")

        if action == "cancel":
            if order.status != "PENDENTE":
                raise UnprocessableEntityError("Esse pedido não pode ser cancelado")

            self.__order_repository.update_order_status(order_id=order_id, new_status=OrderStatus.CANCELLED)

        elif action == "pay":
            if order.status != "PENDENTE":
                raise UnprocessableEntityError("Esse pedido não pode ser pago")

            self.__order_repository.update_order_status(order_id=order_id, new_status=OrderStatus.PAID)

        else:
            raise BadRequestError("Opção inválida")

    def delete_order(self, order_id: int):
        """
        Remove um pedido do sistema pelo seu ID.
        Apenas administradores podem realizar essa operação.

        Requer autenticação e cargo 'admin'.

        Args:
            id (int): ID do pedido a ser deletado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                         {"status": "OK", "message": "Pedido deletado com sucesso."}
        """
        order = self.__order_repository.get_order_by_id(order_id=order_id)

        if not order:
            raise NotFoundError("Pedido não encontrado")

        self.__order_repository.delete_order(order_id=order_id)