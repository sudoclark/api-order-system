from flask import request
from flask_login import current_user
import bcrypt

from src.models.mysql.repositories.user_repository import UserRepository
from utils.ApiUtils import ApiUtils

resp = ApiUtils.response

class UserController:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    def create_user(self, request):
        response = request.json

        if not response or "username" not in response or "password" not in response:
            raise Exception("ERROR: Dados inválidos. Verifique as informações enviadas")

        username = response.get("username")
        password = response.get("password")

        if not username or not password:
            raise Exception("ERROR: Credenciais inválidas")

        hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        self.__user_repository.create_user(username=username, password=hashed)

    def get_users(self):
        if current_user.role == "user":
            user = self.__user_repository.get_user_by_id(current_user.id)
            return user.to_dict()

        users = self.__user_repository.get_users()

        return [user.to_dict() for user in users]

    def get_user_by_id(self, user_id: int):
        if current_user.role == "user" and current_user.id != user_id:
            raise Exception("Você não tem permissão para ver informações de outros usuários") 

        user = self.__user_repository.get_user_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        return user.to_dict()

    def update_user(self, user_id: int, request: dict):
        if current_user.role == "user" and current_user.id != user_id:
            raise Exception("Você não tem permissão para editar informações de outros usuários")

        response = request.json

        if not response:
            raise Exception("Dados inválidos")
        password = response.get("password")


        if password:
            hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        user = self.__user_repository.get_user_by_id(user_id)

        if not user:
            raise Exception("Usuário não encontrado")

        fields = ["username", "password", "role"]
        updates = {}

        for field in fields:
            if field in response:
                if not response[field]:
                    raise Exception("Dados inválidos. Verifique as informações enviadas")

                if current_user.role == "user" and field == "role":
                    raise Exception("Você não tem permissão para alterar o seu cargo no sistema. Solicite a um admin")

                updates[field] = response[field] if field != "password" else hashed

        self.__user_repository.update_user(user_id, updates)

    def delete_user(self, user_id: int):
        if current_user.role == "user" and current_user.id != user_id:
            raise Exception("Você não tem permissão para deletar outros usuários do sistema")

        self.__user_repository.delete_user(user_id)