from flask_login import login_required
from flask_login import current_user
import bcrypt

from src.errors.http_errors.not_found_error import NotFoundError
from src.errors.http_errors.forbidden_error import ForbiddenError
from src.errors.http_errors.bad_request_error import BadRequestError
from src.models.interfaces.user_repository_interface import UserRepositoryInterface

class UserController:
    def __init__(self, user_repository: UserRepositoryInterface):
        self.__user_repository = user_repository

    def create_user(self, request):
        """
        Cria um novo usuário no sistema com cargo padrão 'user'.
        Verifica se os campos 'username' e 'password' estão presentes na requisição e não estão vazios.
        A senha é criptografada com bcrypt antes de ser armazenada no banco de dados.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Dados inválidos. Verifique as informações enviadas."}
                         {"status": "OK", "message": "Usuário criado com sucesso."}
        """
        response = request.json

        if not response or "username" not in response or "password" not in response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

        username = response.get("username")
        password = response.get("password")

        if not username or not password:
            raise BadRequestError("Credenciais inválidas. Verifique as informações enviadas")

        hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        self.__user_repository.create_user(username=username, password=hashed)

    @login_required
    def get_users(self):
        """
        Retorna a listagem de usuários do sistema.
        Usuários com cargo 'user' recebem apenas suas próprias informações.
        Usuários com cargo 'admin' recebem a listagem completa de todos os usuários.

        Requer autenticação.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Usuário obtido com sucesso.", "user": {...}}
                         {"status": "OK", "message": "Listagem realizada com sucesso.", "users": [...]}
        """
        if current_user.role == "user":
            user = self.__user_repository.get_user_by_id(current_user.id)
            return [user.to_dict()]

        users = self.__user_repository.get_users()

        return [user.to_dict() for user in users]

    @login_required
    def get_user_by_id(self, user_id: int):
        """
        Retorna as informações de um usuário específico pelo seu ID.
        Usuários com cargo 'user' só podem consultar suas próprias informações.
        Usuários com cargo 'admin' podem consultar qualquer usuário.

        Requer autenticação.

        Args:
            id (int): ID do usuário a ser consultado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                         {"status": "OK", "message": "Usuário obtido com sucesso.", "user": {...}}
        """
        if current_user.role == "user" and current_user.id != user_id:
            raise ForbiddenError("Você não tem permissão para ver informações de outros usuários") 

        user = self.__user_repository.get_user_by_id(user_id)

        if not user:
            raise NotFoundError("Usuário não encontrado")

        return user.to_dict()

    @login_required
    def update_user(self, user_id: int, request: dict):
        """
        Atualiza os dados de um usuário específico pelo seu ID.
        Usuários com cargo 'user' só podem alterar suas próprias informações e não podem alterar o campo 'role'.
        Usuários com cargo 'admin' podem alterar qualquer usuário, incluindo o cargo.
        Caso o campo 'password' seja enviado, a nova senha é criptografada com bcrypt antes de ser salva.

        Requer autenticação.

        Args:
            id (int): ID do usuário a ser atualizado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                         {"status": "OK", "message": "Dados alterados com sucesso."}
        """
        if current_user.role == "user" and current_user.id != user_id:
            raise ForbiddenError("Você não tem permissão para editar informações de outros usuários")

        response = request.json

        if not response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

        password = response.get("password")

        if password:
            hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        user = self.__user_repository.get_user_by_id(user_id)

        if not user:
            raise NotFoundError("Usuário não encontrado")

        fields = ["username", "password", "role"]
        updates = {}

        for field in fields:
            if field in response:
                if not response[field]:
                    raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

                if current_user.role == "user" and field == "role":
                    raise ForbiddenError("Você não tem permissão para alterar o seu cargo no sistema. Solicite a um admin")

                updates[field] = response[field] if field != "password" else hashed

        self.__user_repository.update_user(user_id, updates)

    @login_required
    def delete_user(self, user_id: int):
        """
        Remove um usuário do sistema pelo seu ID.
        Usuários com cargo 'user' só podem deletar a si mesmos.
        Usuários com cargo 'admin' podem deletar qualquer usuário.

        Requer autenticação.

        Args:
            id (int): ID do usuário a ser deletado.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                         {"status": "OK", "message": "Usuário deletado com sucesso."}
        """
        if current_user.role == "user" and current_user.id != user_id:
            raise ForbiddenError("Você não tem permissão para deletar outros usuários do sistema")

        self.__user_repository.delete_user(user_id)