import os
from flask import Flask
from dotenv import load_dotenv
from src.utils.database import db
from flask_login import LoginManager

from src.routes.user_routes import user_bp
from src.routes.auth_routes import auth_bp
from src.routes.order_routes import orders_bp
from src.routes.products_routes import products_bp
from src.models.mysql.settings.base import Base
from src.models.mysql.entities.user import User
from src.models.mysql.entities.order import Order, OrderItem
from src.models.mysql.entities.product import Product
from src.models.mysql.settings.connect import db_manager_connection
from src.models.mysql.repositories.auth_repository import AuthRepository

load_dotenv()

app = Flask(__name__)

app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(products_bp)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"

db_manager_connection.create_engine()

with app.app_context():
    Base.metadata.create_all(bind=db_manager_connection._DbManager__engine)

@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    auth_repository = AuthRepository(db_manager_connection)
    user = auth_repository.get_user_by_id(user_id)

    return user