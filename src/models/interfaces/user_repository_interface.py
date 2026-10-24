from abc import ABC, abstractmethod

class UserRepositoryInterface(ABC):
    @abstractmethod
    def create_user(self, username: str, password: str) -> None: pass

    @abstractmethod
    def get_users(self) -> list: pass

    @abstractmethod
    def get_user_by_id(self, user_id: int): pass

    @abstractmethod
    def update_user(self, user_id: int, fields: dict) -> None: pass

    @abstractmethod
    def delete_user(self, user_id: int) -> None: pass