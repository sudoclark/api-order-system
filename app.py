from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
import pymysql

from models.Tables import User, Product, OrderItem, Order
from database import db
from utils.ApiUtils import ApiUtils

# ===========================================
# CONFIGURAÇÃO - Configuração inicial da API
# ===========================================

app = Flask(__name__)
resp = ApiUtils.response

app.config["SECRET_KEY"] = "my-super-secure-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:pass@127.0.0.1:3306/database"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"




# ================================================
# AUTENTICAÇÃO - Rotas de autenticação do usuário
# ================================================

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)

    return user


@app.route("/login", methods=["POST"])
def login():
    response = request.json

    if not response or "username" not in response or "password" not in response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas!")), 400
    
    username = response.get("username")
    password = response.get("password")

    if not username or not password:
        return jsonify(resp("ERROR", "Credenciais inválidas!")), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado!")), 404
    
    if not bcrypt.checkpw(str.encode(password), user.password):
        return jsonify(resp("ERROR", "Credenciais inválidas!")), 401
    
    login_user(user)

    return jsonify(resp("OK", "Usuário autenticado com sucesso!"))


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()

    return jsonify(resp("OK", "Usuário deslogado com sucesso!"))




