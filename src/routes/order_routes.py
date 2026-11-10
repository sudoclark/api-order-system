from flask import Blueprint, request, jsonify
from flask_login import login_required

from src.utils.ApiUtils import ApiUtils
from src.errors.handle_error import handle_error
from src.controllers.order_controller import OrderController
from src.models.mysql.settings.connect import db_manager_connection
from src.utils.decorators.admin_required_decorator import admin_required
from src.models.mysql.repositories.order_repository import OrderRepository
from src.models.mysql.repositories.product_repository import ProductRepository

product_repository = ProductRepository(db_manager_connection)
order_repository = OrderRepository(db_manager_connection)
order_controller = OrderController(order_repository, product_repository)

resp = ApiUtils.response

orders_bp = Blueprint("orders_routes_bp", __name__)

# ===========================================================
# ORDER_ITEM - Rotas relacionadas aos produtos de um pedido
# ===========================================================

@orders_bp.route("/order-item", methods=["POST"])
@login_required
def add_item():
    try:
        order_controller.add_item(request)
        return jsonify(resp("OK", "Produto adicionado ao pedido")), 201

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order-item/<int:order_item_id>", methods=["PATCH"])
@login_required
def update_order_item(order_item_id):
    try:
        order_controller.update_order_item(request, order_item_id)
        return jsonify(resp("OK", "Quantidade alterada com sucesso"))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order-item/<int:order_item_id>", methods=["DELETE"])
@login_required
def delete_order_item(order_item_id):
    try:
        order_controller.delete_order_item(order_item_id)
        return jsonify(resp("OK", "Produto deletado com sucesso"))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]



# ===========================================================
# ORDER - Rotas relacionadas aos pedidos no sistema
# ===========================================================

@orders_bp.route("/order", methods=["POST"])
@login_required
def create_order():
    try:
        order_controller.create_order()
        return jsonify(resp("OK", "Pedido criado com sucesso.")), 201

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order", methods=["GET"])
@login_required
@admin_required
def get_orders():
    try:
        orders = order_controller.get_orders()
        return jsonify(resp("OK", "Listagem obtida com sucesso.", orders=orders))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order/<int:order_id>", methods=["GET"])
@login_required
def get_order_by_id(order_id):
    try:
        order = order_controller.get_order_by_id(order_id)
        return jsonify(resp("OK", "Pedido obtido com sucesso.", order=order))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order/user", methods=["GET"])
@login_required
def get_orders_from_specific_user():
    try:
        orders = order_controller.get_orders_from_specif_user()
        return jsonify(resp("OK", "Listagem obtida com sucesso.", orders=orders))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order/<int:order_id>/order-items", methods=["GET"])
@login_required
def get_orderItems_from_specific_order(order_id):
    try:
        order_itens = order_controller.get_orderItems_from_specific_order(order_id)
        return jsonify(resp("OK", "Listagem obtida com sucesso.", order_items=order_itens))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order/<action>/<int:order_id>", methods=["PATCH"])
@login_required
@admin_required
def update_order_status(action, order_id):
    try:
        order_controller.update_order_status(action, order_id)
        return jsonify(resp("OK", "Status atualizado com sucesso."))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@orders_bp.route("/order/<int:order_id>", methods=["DELETE"])
@login_required
@admin_required
def delete_order(order_id):
    try:
        order_controller.delete_order(order_id)
        return jsonify(resp("OK", "Pedido deletado com sucesso."))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]
