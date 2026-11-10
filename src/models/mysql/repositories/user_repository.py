from src.models.mysql.entities.user import User
from src.models.mysql.settings.connect import DbManager
from src.models.interfaces.user_repository_interface import UserRepositoryInterface

class UserRepository(UserRepositoryInterface):
    def __init__(self, db_connection: DbManager):
        self.__db_connection = db_connection

    def create_user(self, username: str, password: str) -> None:
        try:
            with self.__db_connection as db:
                user = User(username=username, password=password, role="user")

                db.session.add(user)
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def get_users(self) -> list:
        with self.__db_connection as db:
            users = db.session.query(User).all()
            return users

    def get_user_by_id(self, user_id: int) -> User:
        with self.__db_connection as db:
            user = db.session.query(User).filter(User.id == user_id).first()
            return user

    def update_user(self, user_id: int, fields: dict) -> None:
        try:
            with self.__db_connection as db:
                user = db.session.query(User).filter(User.id == user_id).first()

                for field, value in fields.items():
                    setattr(user, field, value)

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def delete_user(self, user_id: int) -> None:
        try:
            with self.__db_connection as db:
                db.session.query(User).filter(User.id == user_id).delete()

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex