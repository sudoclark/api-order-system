from abc import ABC, abstractmethod
from src.models.mysql.entities.user import User

class AuthRepositoryInterface(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> User:
        pass
