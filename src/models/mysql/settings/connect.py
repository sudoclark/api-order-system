import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class DbManager:
    def __init__(self):
        self.__database_url = DATABASE_URL
        self.__engine = None
        self.session = None

    def create_engine(self):
        self.__engine = create_engine(self.__database_url)

    def __enter__(self):
        make_session = sessionmaker()
        self.session = make_session(bind=self.__engine)
        return self

    def __exit__(self, exc_type, exc, tb):
        """
        Quando o session.close() é chamado, o SQLAlchemy expira todos os objetos,
        basicamente apara todos os dados na memória. O expunge_all() desanexa os objetos
        antes de fechar a sessão, ou seja, os dados continuam na memória, o objeto só deixa
        de ser monitorado pela sessão.

        Essa mudança foi feita por conta do endpoint orders/user — quando eu buscava os
        pedidos de um usuário, dava erro, pois o repositório buscava o pedido mas quando
        tentava buscar o order.user, os dados já tinham sido apagados pelo session.close(),
        ele tentava fazer a query novamente, mas como a sessão já tinha sido fechada, dava
        erro. Com o expunge_all(), esses dados ficam salvos e conseguem ser processados.
        """
        self.session.expunge_all()
        self.session.close()

db_manager_connection = DbManager()
