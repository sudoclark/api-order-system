from src.errors.http_errors.not_found_error import NotFoundError
from src.errors.http_errors.bad_request_error import BadRequestError
from src.errors.http_errors.unprocessable_entity_error import UnprocessableEntityError
from src.models.interfaces.product_repository_interface import ProductRepositoryInterface

class ProductController:
    def __init__(self, product_repository: ProductRepositoryInterface):
        self.__product_repository = product_repository

    def create_product(self, request):
        """
        Cria um novo produto no sistema.
        Verifica se os campos 'name' e 'price' estão presentes na requisição e não estão vazios.
        Impede o cadastro de produtos com nomes duplicados.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Produto já existe."}
                         {"status": "OK", "message": "Produto adicionado com sucesso."}
        """
        response = request.json

        if not response or "name" not in response or "price" not in response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

        name = response.get("name")
        price = response.get("price")

        if not name or not price:
            raise BadRequestError("Dados inválidos, o nome e o valor do produto são obrigatórios")

        exists = self.__product_repository.get_product_by_name(name)

        if exists:
            raise UnprocessableEntityError("Produto já existe")

        self.__product_repository.create_product(name=name, price=price)

    def get_products(self):
        """
        Retorna a listagem de todos os produtos cadastrados no sistema.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "products": [...]}
        """
        products = self.__product_repository.get_products()

        return [p.to_dict() for p in products]

    def get_product_by_id(self, product_id: int):
        """
        Retorna as informações de um produto específico pelo seu ID.

        Requer autenticação.

        Args:
            id (int): ID do produto a ser consultado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Produto não encontrado."}
                         {"status": "OK", "message": "Produto obtido com sucesso.", "product": {...}}
        """
        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise NotFoundError("Produto não encontrado")

        return product.to_dict()

    def update_product(self, request, product_id: int):
        """
        Atualiza os dados de um produto específico pelo seu ID.
        Os campos atualizáveis são 'name' e 'price'.
        Apenas administradores podem realizar essa operação.

        Requer autenticação e cargo 'admin'.

        Args:
            id (int): ID do produto a ser atualizado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Produto não encontrado."}
                         {"status": "OK", "message": "Produto alterado com sucesso."}
        """
        response = request.json

        if not response:
            raise BadRequestError("Dados inválidos, verifique as informações enviadas")

        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise NotFoundError("Produto não encontrado")

        fields = ["name", "price"]

        values_to_apply = {}
        for field in fields:
            if field in response:
                if not response[field]:
                    raise BadRequestError("Dados inválidos. Tem certeza que enviou nome ou preço do produto?")

                values_to_apply[field] = response[field]

        if not values_to_apply:
            raise UnprocessableEntityError("Nenhum campo válido enviado")

        self.__product_repository.update_product(product_id, values_to_apply)

    def delete_product(self, product_id: int):
        """
        Remove um produto do sistema pelo seu ID.
        Apenas administradores podem realizar essa operação.

        Requer autenticação e cargo 'admin'.

        Args:
            id (int): ID do produto a ser deletado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Produto não encontrado."}
                         {"status": "OK", "message": "Produto deletado com sucesso."}
        """
        product = self.__product_repository.get_product_by_id(product_id)

        if not product:
            raise NotFoundError("Produto não encontrado")

        self.__product_repository.delete_product(product_id)