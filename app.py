from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
import pymysql
from functools import wraps
import os
from dotenv import load_dotenv

from models.Tables import User, Product, OrderItem, Order
from OrderStatus import OrderStatus
from database import db
from utils.ApiUtils import ApiUtils

# ==========================================================
# CONFIGURAÇÃO - Configuração inicial da API
# ==========================================================

load_dotenv()

app = Flask(__name__)
resp = ApiUtils.response

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL")  # BANCO DE TESTES

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "login"



def admin_required(func):
    """
    Decorator que restringe o acesso de uma rota apenas a usuários com cargo 'admin'.
    Verifica o cargo do usuário autenticado e rejeita a requisição caso não seja admin.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Você não tem permissão para realizar essa ação. Consulte um admin do sistema"}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != "admin":
            return jsonify(resp("ERROR", "Você não tem permissão para realizar essa ação. Consulte um admin do sistema")), 403
        return func(*args, **kwargs)
    return wrapper




# ==========================================================
# AUTENTICAÇÃO - Rotas de autenticação do usuário
# ==========================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Carrega o usuário a partir do ID armazenado na sessão.
    Utilizado pelo Flask-Login para gerenciar a autenticação entre requisições.

    Args:
        user_id (int): ID do usuário armazenado na sessão.

    Returns:
        User | None: Instância do usuário encontrado ou None caso não exista.
    """
    user = User.query.get(user_id)

    return user


@app.route("/login", methods=["POST"])
def login():
    """
    Realiza o login do usuário no sistema.
    Verifica se os campos 'username' e 'password' estão presentes na requisição e não estão vazios,
    se o usuário existe no banco de dados e se a senha fornecida corresponde à senha cadastrada.
    Utiliza bcrypt para validar a senha, que é armazenada de forma criptografada no banco de dados.
    Se as credenciais forem válidas, autentica o usuário na sessão.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Credenciais inválidas."}
                     {"status": "OK", "message": "Usuário autenticado com sucesso."}
    """
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
@login_required
def logout():
    """
    Realiza o logout do usuário autenticado, encerrando sua sessão no sistema.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Usuário deslogado com sucesso."}
    """
    logout_user()

    return jsonify(resp("OK", "Usuário deslogado com sucesso."))




# ==========================================================
# USER - Rotas relacionadas aos usuários no sistema
# ==========================================================

@app.route("/users", methods=["POST"])
def create_user():
    """
    Cria um novo usuário no sistema com cargo padrão 'user'.
    Verifica se os campos 'username' e 'password' estão presentes na requisição e não estão vazios.
    A senha é criptografada com bcrypt antes de ser armazenada no banco de dados.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Dados inválidos. Verifique as informações enviadas."}
                     {"status": "OK", "message": "Usuário criado com sucesso."}
    """
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
    """
    Retorna a listagem de usuários do sistema.
    Usuários com cargo 'user' recebem apenas suas próprias informações.
    Usuários com cargo 'admin' recebem a listagem completa de todos os usuários.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Usuário obtido com sucesso.", "user": {...}}
                     {"status": "OK", "message": "Listagem realizada com sucesso.", "users": [...]}
    """
    if current_user.role == "user":
        return jsonify(resp("OK", "Usuário obtido com sucesso.", user=current_user.to_dict()))

    users = User.query.all()

    return jsonify(resp("OK", "Listagem realizada com sucesso.", users=[user.to_dict() for user in users]))


@app.route("/users/<int:id>", methods=["GET"])
@login_required
def get_user_by_id(id):
    """
    Retorna as informações de um usuário específico pelo seu ID.
    Usuários com cargo 'user' só podem consultar suas próprias informações.
    Usuários com cargo 'admin' podem consultar qualquer usuário.

    Requer autenticação.

    Args:
        id (int): ID do usuário a ser consultado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                     {"status": "OK", "message": "Usuário obtido com sucesso.", "user": {...}}
    """
    if current_user.role == "user" and current_user.id != id:
        return jsonify(resp("OK", "Você não tem permissão para ver informações de outros usuários.", user=current_user.to_dict())), 403

    user = User.query.get(id)

    if not user:
        return jsonify(resp("ERROR", "Usuário não encontrado.")), 404

    return jsonify(resp("OK", "Usuário obtido com sucesso.", user=user.to_dict()))


@app.route("/users/<int:id>", methods=["PATCH"])
@login_required
def update_user(id):
    """
    Atualiza os dados de um usuário específico pelo seu ID.
    Usuários com cargo 'user' só podem alterar suas próprias informações e não podem alterar o campo 'role'.
    Usuários com cargo 'admin' podem alterar qualquer usuário, incluindo o cargo.
    Caso o campo 'password' seja enviado, a nova senha é criptografada com bcrypt antes de ser salva.

    Requer autenticação.

    Args:
        id (int): ID do usuário a ser atualizado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                     {"status": "OK", "message": "Dados alterados com sucesso."}
    """
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
    """
    Remove um usuário do sistema pelo seu ID.
    Usuários com cargo 'user' só podem deletar a si mesmos.
    Usuários com cargo 'admin' podem deletar qualquer usuário.

    Requer autenticação.

    Args:
        id (int): ID do usuário a ser deletado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Usuário não encontrado."}
                     {"status": "OK", "message": "Usuário deletado com sucesso."}
    """
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
    """
    Cria um novo produto no sistema.
    Verifica se os campos 'name' e 'price' estão presentes na requisição e não estão vazios.
    Impede o cadastro de produtos com nomes duplicados.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Produto já existe."}
                     {"status": "OK", "message": "Produto adicionado com sucesso."}
    """
    response = request.json

    if not response or "name" not in response or "price" not in response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas.")), 400

    name = response.get("name")
    price = response.get("price")

    if not name and not price:
        return jsonify(resp("ERROR", "Dados inválidos, o nome e o valor do produto são obrigatórios.")), 400

    exists = Product.query.filter_by(name=name).first()

    if exists:
        return jsonify(resp("ERROR", "Produto já existe.")), 400

    try:
        product = Product(name=name, price=price)

        db.session.add(product)
        db.session.commit()

        return jsonify(resp("OK", "Produto adicionado com sucesso.")), 201

    except ValueError as e:
        return jsonify(resp("ERROR", str(e))), 400


@app.route("/products", methods=["GET"])
@login_required
def get_products():
    """
    Retorna a listagem de todos os produtos cadastrados no sistema.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "products": [...]}
    """
    products = Product.query.all()

    return jsonify(resp("OK", "Listagem obtida com sucesso.", products=[p.to_dict() for p in products]))


@app.route("/products/<int:id>", methods=["GET"])
@login_required
def get_product_by_id(id):
    """
    Retorna as informações de um produto específico pelo seu ID.

    Requer autenticação.

    Args:
        id (int): ID do produto a ser consultado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Produto não encontrado."}
                     {"status": "OK", "message": "Produto obtido com sucesso.", "product": {...}}
    """
    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404

    return jsonify(resp("OK", "Produto obtido com sucesso.", product=product.to_dict()))


@app.route("/products/<int:id>", methods=["PATCH"])
@login_required
@admin_required
def update_product(id):
    """
    Atualiza os dados de um produto específico pelo seu ID.
    Os campos atualizáveis são 'name' e 'price'.
    Apenas administradores podem realizar essa operação.

    Requer autenticação e cargo 'admin'.

    Args:
        id (int): ID do produto a ser atualizado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Produto não encontrado."}
                     {"status": "OK", "message": "Produto alterado com sucesso."}
    """
    response = request.json

    if not response:
        return jsonify(resp("ERROR", "Dados inválidos, verifique as informações enviadas.")), 400

    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404

    fields = ["name", "price"]

    values_to_apply = {}
    for field in fields:
        if field in response:
            if not response[field]:
                return jsonify(resp("ERROR", "Dados inválidos. Tem certeza que enviou nome ou preço do produto?")), 400
            values_to_apply[field] = response[field]

    if not values_to_apply:
        return jsonify(resp("ERROR", "Nenhum campo válido enviado.")), 400

    try:
        for field, value in values_to_apply.items():
            setattr(product, field, value)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify(resp("ERROR", str(e))), 400

    return jsonify(resp("OK", "Produto alterado com sucesso."))


@app.route("/products/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_product(id):
    """
    Remove um produto do sistema pelo seu ID.
    Apenas administradores podem realizar essa operação.

    Requer autenticação e cargo 'admin'.

    Args:
        id (int): ID do produto a ser deletado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Produto não encontrado."}
                     {"status": "OK", "message": "Produto deletado com sucesso."}
    """
    product = Product.query.get(id)

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify(resp("OK", "Produto deletado com sucesso."))




# ===========================================================
# ORDER_ITEM - Rotas relacionadas aos produtos de um pedido
# ===========================================================

@app.route("/order-item", methods=["POST"])
@login_required
def add_item():
    """
    Adiciona um produto a um pedido em aberto (status 'PENDENTE') do usuário autenticado.
    Verifica se os campos 'quantity' e 'product_name' estão presentes na requisição e não estão vazios.
    A quantidade deve ser um número inteiro e o produto deve existir no sistema.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Pedido não encontrado. Certifique-se que esse usuário já possui um pedido em aberto no sistema"}
                     {"status": "OK", "message": "Produto adicionado ao pedido"}
    """
    response = request.json

    if not response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas!")), 400

    qtt = response.get("quantity")
    product_name = response.get("product_name")

    if not qtt or not product_name:
        return jsonify(resp("ERROR", "Dados inválidos, a quantidade e o nome do produto são obrigatórios!")), 400

    if not isinstance(qtt, int):
        return jsonify(resp("ERROR", "A quantidade precisa ser um número inteiro.")), 400

    order = Order.query.filter(Order.status=="PENDENTE", Order.user_id==current_user.id).first()

    if not order:
        return jsonify(resp("ERROR", "Pedido não encontrado. Certifique-se que esse usuário já possui um pedido em aberto no sistema")), 404

    product = Product.query.filter_by(name=product_name).first()

    if not product:
        return jsonify(resp("ERROR", "Produto não encontrado, verifique as informações enviadas.")), 404

    order_item = OrderItem(quantity=qtt, order_id=order.id, product_id=product.id)

    db.session.add(order_item)
    db.session.commit()

    return jsonify(resp("OK", "Produto adicionado ao pedido")), 201


@app.route("/order-item/<int:id>", methods=["PATCH"])
@login_required
def update_order_item(id):
    """
    Atualiza a quantidade de um item em um pedido pelo ID do item.
    O usuário autenticado só pode alterar itens de seus próprios pedidos.
    O campo 'quantity' deve ser um número inteiro.

    Requer autenticação.

    Args:
        id (int): ID do item do pedido a ser atualizado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Você não pode alterar o pedido de outra pessoa."}
                     {"status": "OK", "message": "Quantidade alterada com sucesso."}
    """
    response = request.json

    if not response:
        return jsonify(resp("ERROR", "Dados inválidos. Verifique as informações enviadas!")), 400

    order_item = OrderItem.query.get(id)

    if not order_item:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404

    if order_item.order_id not in current_user.orders:
        return jsonify(resp("ERROR", "Você não pode alterar o pedido de outra pessoa.")), 403

    if not isinstance(response["quantity"], int):
        return jsonify(resp("ERROR", "A quantidade precisa ser um número inteiro.")), 400

    order_item.quantity = response["quantity"]

    db.session.commit()

    return jsonify(resp("OK", "Quantidade alterada com sucesso."))


@app.route("/order-item/<int:id>", methods=["DELETE"])
@login_required
def delete_order_item(id):
    """
    Remove um item de um pedido pelo seu ID.
    O usuário autenticado só pode remover itens de seus próprios pedidos.

    Requer autenticação.

    Args:
        id (int): ID do item do pedido a ser removido.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Você não pode deletar o pedido de outra pessoa."}
                     {"status": "OK", "message": "Produto deletado com sucesso."}
    """
    order_item = OrderItem.query.get(id)

    if not order_item:
        return jsonify(resp("ERROR", "Produto não encontrado.")), 404

    if order_item.order_id not in current_user.orders:
        return jsonify(resp("ERROR", "Você não pode deletar o pedido de outra pessoa.")), 403

    db.session.delete(order_item)
    db.session.commit()

    return jsonify(resp("OK", "Produto deletado com sucesso."))




# ===========================================================
# ORDER - Rotas relacionadas aos pedidos no sistema
# ===========================================================

@app.route("/order", methods=["POST"])
@login_required
def create_order():
    """
    Cria um novo pedido para o usuário autenticado com status inicial 'PENDENTE'.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Pedido criado com sucesso."}
    """
    order = Order(user_id=current_user.id)

    db.session.add(order)
    db.session.commit()

    return jsonify(resp("OK", "Pedido criado com sucesso.")), 201


@app.route("/order", methods=["GET"])
@login_required
@admin_required
def get_orders():
    """
    Retorna a listagem de todos os pedidos cadastrados no sistema.
    Apenas administradores podem realizar essa operação.

    Requer autenticação e cargo 'admin'.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "orders": [...]}
    """
    orders = Order.query.all()

    return jsonify(resp("OK", "Listagem obtida com sucesso.", orders=[order.to_dict() for order in orders]))


@app.route("/order/<int:id>", methods=["GET"])
@login_required
def get_order_by_id(id):
    """
    Retorna as informações de um pedido específico pelo seu ID.
    Usuários com cargo 'user' só podem consultar seus próprios pedidos.
    Usuários com cargo 'admin' podem consultar qualquer pedido.

    Requer autenticação.

    Args:
        id (int): ID do pedido a ser consultado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                     {"status": "OK", "message": "Pedido obtido com sucesso.", "order": {...}}
    """
    order = Order.query.get(id)

    if not order:
        return jsonify(resp("ERROR", "Pedido não encontrado.")), 404

    if current_user.role != "admin" and current_user.id != order.user_id:
        return jsonify(resp("ERROR", "Você não tem permissão para visualizar um pedido de outro usuário. Verifique com um admin.")), 403

    return jsonify(resp("OK", "Pedido obtido com sucesso.", order=order.to_dict()))


@app.route("/order/user", methods=["GET"])
@login_required
def get_orders_from_specific_user():
    """
    Retorna a listagem de todos os pedidos do usuário autenticado.

    Requer autenticação.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "OK", "message": "Listagem obtida com sucesso.", "orders": [...]}
    """
    orders = current_user.orders

    return jsonify(resp("OK", "Listagem obtida com sucesso.", orders=[ord.to_dict() for ord in orders]))


@app.route("/order/<int:id>/order-items", methods=["GET"])
@login_required
def get_orderItems_from_specific_order(id):
    """
    Retorna a listagem de todos os itens de um pedido específico pelo ID do pedido.
    Usuários com cargo 'user' só podem consultar itens de seus próprios pedidos.

    Requer autenticação.

    Args:
        id (int): ID do pedido cujos itens serão listados.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                     {"status": "ERROR", "message": "Você não pode visualizar itens dos pedidos de outros usuários."}
                     {"status": "OK", "message": "Listagem obtida com sucesso.", "order_items": [...]}
    """
    order = Order.query.get(id)

    if not order:
        return jsonify(resp("ERROR", "Pedido não encontrado.")), 404
    
    if current_user.id != order.user_id:
        return jsonify(resp("ERROR", "Você não pode visualizar itens dos pedidos de outros usuários."))

    order_items = order.order_items

    return jsonify(resp("OK", "Listagem obtida com sucesso.", order_items=[oi.to_dict() for oi in order_items]))


@app.route("/order/<action>/<int:id>", methods=["PATCH"])
@login_required
@admin_required
def update_order_status(action, id):
    """
    Atualiza o status de um pedido pelo seu ID com base na ação informada.
    As ações válidas são 'cancel' (cancela o pedido) e 'pay' (marca o pedido como pago).
    Ambas as ações só podem ser executadas em pedidos com status 'PENDENTE'.
    Apenas administradores podem realizar essa operação.

    Requer autenticação e cargo 'admin'.

    Args:
        action (str): Ação a ser realizada no pedido. Valores aceitos: 'cancel', 'pay'.
        id (int): ID do pedido a ser atualizado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                     {"status": "ERROR", "message": "Opção inválida."}
                     {"status": "OK", "message": "Pedido cancelado com sucesso."}
                     {"status": "OK", "message": "Pedido pago com sucesso."}
    """
    order = Order.query.get(id)

    if not order:
        return jsonify(resp("ERROR", "Pedido não encontrado.")), 404

    if action == "cancel":
        if order.status != "PENDENTE":
            return jsonify(resp("ERROR", "Esse pedido não pode ser cancelado.", order_status=order.status)), 400

        order.status = OrderStatus.CANCELLED
        db.session.commit()

        return jsonify(resp("OK", "Pedido cancelado com sucesso."))

    elif action == "pay":
        if order.status != "PENDENTE":
            return jsonify(resp("ERROR", "Esse pedido não pode ser pago.", order_status=order.status)), 400

        order.status = OrderStatus.PAID
        db.session.commit()

        return jsonify(resp("OK", "Pedido pago com sucesso."))

    else:
        return jsonify(resp("ERROR", "Opção inválida.")), 400



@app.route("/order/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_order(id):
    """
    Remove um pedido do sistema pelo seu ID.
    Apenas administradores podem realizar essa operação.

    Requer autenticação e cargo 'admin'.

    Args:
        id (int): ID do pedido a ser deletado.

    Returns:
        JSON(response): Uma mensagem formatada em JSON que consta o status da operação e um complemento.
            Example: {"status": "ERROR", "message": "Pedido não encontrado."}
                     {"status": "OK", "message": "Pedido deletado com sucesso."}
    """
    order = Order.query.get(id)

    if not order:
        return jsonify(resp("ERROR", "Pedido não encontrado.")), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify(resp("OK", "Pedido deletado com sucesso."))




if __name__ == "__main__":
    app.run(debug=True)
