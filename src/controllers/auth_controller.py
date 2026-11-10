import bcrypt
from flask_login import login_user, logout_user

from src.errors.http_errors.not_found_error import NotFoundError
from src.errors.http_errors.bad_request_error import BadRequestError
from src.models.interfaces.auth_repository_interface import AuthRepositoryInterface

class AuthController:
    def __init__(self, auth_repository: AuthRepositoryInterface):
        self.__auth_repository = auth_repository

    def login(self, request):
        """
        Realiza o login do usuário no sistema.
        Verifica se os campos 'username' e 'password' estão presentes na requisição e não estão vazios,
        se o usuário existe no banco de dados e se a senha fornecida corresponde à senha cadastrada.
        Utiliza bcrypt para validar a senha, que é armazenada de forma criptografada no banco de dados.
        Se as credenciais forem válidas, autentica o usuário na sessão.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "ERROR", "message": "Credenciais inválidas."}
                        {"status": "OK", "message": "Usuário autenticado com sucesso."}
        """
        response = request.json

        if not response or "username" not in response or "password" not in response:
            raise BadRequestError("Dados inválidos. Verifique as informações enviadas")

        username = response.get("username")
        password = response.get("password")

        if not username or not password:
            raise BadRequestError("Credenciais inválidas")

        user = self.__auth_repository.get_user_by_username(username)

        if not user:
            raise NotFoundError("Usuário não encontrado")

        if not bcrypt.checkpw(str.encode(password), user.password):
            raise BadRequestError("Credenciais inválidas")

        login_user(user)

    def logout(self):
        """
        Realiza o logout do usuário autenticado, encerrando sua sessão no sistema.

        Returns:
            JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
                Example: {"status": "OK", "message": "Usuário deslogado com sucesso."}
        """
        logout_user()