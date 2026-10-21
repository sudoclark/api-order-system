from src.models.mysql.entities.user import User
from src.models.mysql.settings.connect import DbManager

class UserRepository():
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

    def get_user_by_id(self, id: int) -> User:
        with self.__db_connection as db:
            user = db.session.query(User).filter(User.id == id).first()
            return user

    def update_user(self, id: int, field_to_modify: str, value: str) -> None:
        try:
            with self.__db_connection as db:
                user = db.session.query(User).filter(User.id == id).first()

                setattr(user, field_to_modify, value)
                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex

    def delete_user(self, id: int) -> None:
        try:
            with self.__db_connection as db:
                db.session.query(User).filter(User.id == id).delete()

                db.session.commit()
        except Exception as ex:
            db.session.rollback()
            raise ex