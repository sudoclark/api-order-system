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
        self.session.close()

db_manager_connection = DbManager()
