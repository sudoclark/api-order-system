from src.models.interfaces.auth_repository_interface import AuthRepositoryInterface
from src.models.mysql.settings.connect import DbManager
from src.models.mysql.entities.user import User

class AuthRepository(AuthRepositoryInterface):
    def __init__(self, db_connection: DbManager):
        self.__db_connection = db_connection

    def get_user_by_id(self, user_id: int) -> User:
        with self.__db_connection as db:
            user = db.session.query(User).filter(User.id == user_id).first()
            return user

    def get_user_by_username(self, username: str) -> User:
        with self.__db_connection as db:
            user = db.session.query(User).filter(User.username == username).first()
            return user
