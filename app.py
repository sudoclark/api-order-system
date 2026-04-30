from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
import pymysql

from models.Tables import User, Product, OrderItem, Order
from database import db
from utils.ApiUtils import ApiUtils

# ==========================================================
# CONFIGURAÇÃO - Configuração inicial da API
# ==========================================================

app = Flask(__name__)
resp = ApiUtils.response

app.config["SECRET_KEY"] = "my-super-secure-secret-key"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:pass@127.0.0.1:3306/database"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"




# ==========================================================
# AUTENTICAÇÃO - Rotas de autenticação do usuário
# ==========================================================

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)

    return user


@app.route("/login", methods=["POST"])
def login():
    response = request.json

    if not response or "username" not in response or "password" not in response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas.")), 400
    
    username = response.get("username")
    password = response.get("password")

    if not username or not password:
        return jsonify(resp("ERROR", "Credenciais inválidas.")), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado.")), 404
    
    if not bcrypt.checkpw(str.encode(password), user.password):
        return jsonify(resp("ERROR", "Credenciais inválidas.")), 401
    
    login_user(user)

    return jsonify(resp("OK", "Usuário autenticado com sucesso."))


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()

    return jsonify(resp("OK", "Usuário deslogado com sucesso."))




# ==========================================================
# USER - Rotas relacionadas aos usuários no sistema
# ==========================================================

@app.route("/users", methods=["POST"])
def create_user():
    response = request.json

    if not response or "username" not in response or "password" not in response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas.")), 400
    
    username = response.get("username")
    password = response.get("password")

    if not username and not password:
        return jsonify(resp("ERROR", "Credenciais inválidas.")), 400
    
    hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

    user = User(username=username, password=hashed, role="user")

    db.session.add(user)
    db.session.commit()

    return jsonify(resp("OK", "Usuário criado com sucesso.")), 201


@app.route("/users", methods=["GET"])
@login_required
def get_users():
    if current_user.role == "user":
        return jsonify(resp("OK", "Usuário obtido com sucesso.", user=current_user.to_dict()))
    
    users = User.query.all()

    return jsonify(resp("OK", "Listagem realizada com sucesso.", users=[user.to_dict() for user in users]))


@app.route("/users/<int:id>", methods=["GET"])
@login_required
def get_user_by_id(id):
    if current_user.role == "user" and current_user.id != id:
        return jsonify(resp("OK", "Você não tem permissão para ver informações de outros usuários.", user=current_user.to_dict())), 403
    
    user = User.query.get(id)

    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado.")), 404

    return jsonify(resp("OK", "Usuário obtido com sucesso.", user=user.to_dict()))


@app.route("/users/<int:id>", methods=["PATCH"])
@login_required
def update_user(id):
    if current_user.role == "user" and current_user.id != id:
        return jsonify(resp("OK", "Você não tem permissão para editar informações de outros usuários.")), 403
    
    response = request.json
    password = response.get("password")

    if password:
        hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

    if not response:
        return jsonify(resp("ERROR", "Dados inválidos.")), 400
    
    user = User.query.get(id)

    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado.")), 404
    
    fields = ["username", "password", "role"]

    for field in fields:
        if field in response:
            if not response[field]:
                return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas.")), 400
            
            if current_user.role == "user" and field == "role":
                return jsonify(resp("ERROR", "Você não tem permissão para alterar o seu cargo no sistema. Solicite a um admin.")), 403
        
            setattr(user, field, response[field] if field != "password" else hashed)

    db.session.commit()

    return jsonify(resp("OK", "Dados alterados com sucesso."))


@app.route("/users/<int:id>", methods=["DELETE"])
@login_required
def delete_user(id):
    if current_user.role == "user" and current_user.id != id:
        return jsonify(resp("OK", "Você não tem permissão para deletar outros usuários do sistema.")), 403
    
    user = User.query.get(id)

    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado.")), 404
    
    db.session.delete(user)
    db.session.commit()

    return jsonify(resp("OK", "Usuário deletado com sucesso."))




# ==========================================================
# PRODUCTS - Rotas relacionadas aos produtos no sistema
# ==========================================================

@app.route("/products", methods=["POST"])
@login_required
def create_product():
    response = request.json

    if not response or "name" not in response or "price" not in response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas.")), 400
    
    name = response.get("name")
    price = response.get("price")

    if not name and not price:
        return jsonify(resp("ERROR", "Dados inválidos, o nome e o valor do produto são obrigatórios.")), 400
    
    if not isinstance(price, (float, int)) or price <= 0:
        return jsonify(resp("ERROR", "Valor inválido, o preço precisa ser um número positivo maior que zero.")), 400
    
    exists = Product.query.filter_by(name=name).first()

    if exists:
        return jsonify(resp("ERROR", "Produto já existe.")), 400
    
    product = Product(name=name, price=price)

    db.session.add(product)
    db.session.commit()

    return jsonify(resp("OK", "Produto adicionado com sucesso.")), 201


@app.route("/products", methods=["GET"])
@login_required
def get_products():
    products = Product.query.all()

    return jsonify(resp("OK", "Listagem obtida com sucesso.", products=[p.to_dict() for p in products]))


@app.route("/products/<int:id>", methods=["GET"])
@login_required
def get_product_by_id(id):
    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404
    
    return jsonify(resp("OK", "Produto obtido com sucesso.", product=product.to_dict()))


@app.route("/products/<int:id>", methods=["PATCH"])
@login_required
def update_product(id):
    if current_user.role != "admin":
        return jsonify(resp("ERROR", "Você não tem permissão para alterar os dados dos produtos, verifique com um admin.")), 403
    
    response = request.json

    if not response:
        return jsonify(resp("ERROR", "Dados inválidos, verifique as informações enviadas.")), 400
    
    price = response.get("price")

    if price:
        if not isinstance(price, (float, int)) or price < 0:
            return jsonify(resp("ERROR", "O preço precisa ser um número positivo maior que zero.")), 400
    
    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404
    
    fields = ["name", "price"]

    for field in fields:
        if field in response:
            if not response[field]:
                return jsonify(resp("ERROR", "Dados inválidos. Tem certeza que enviou nome ou preço do produto?")), 400
            
            setattr(product, field, response[field])

    db.session.commit()

    return jsonify(resp("OK", "Produto alterado com sucesso."))


@app.route("/products/<int:id>", methods=["DELETE"])
@login_required
def delete_product(id):
    if current_user.role != "admin":
        return jsonify(resp("ERROR", "Você não tem permissão para deletar um produto. Verifique com um admin.")), 403
    
    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404
    
    db.session.delete(product)
    db.session.commit()

    return jsonify(resp("OK", "Produto deletado com sucesso."))



if __name__ == "__main__":
    app.run(debug=True)