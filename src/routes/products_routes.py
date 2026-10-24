from flask import Blueprint, request, jsonify

from utils.ApiUtils import ApiUtils
from src.errors.handle_error import handle_error
from src.models.mysql.settings.connect import db_manager_connection
from src.models.mysql.repositories.product_repository import ProductRepository
from src.controllers.product_controller import ProductController

product_repository = ProductRepository(db_manager_connection)
product_controller = ProductController(product_repository)

resp = ApiUtils.response

products_bp = Blueprint("products_routes_bp", __name__)

@products_bp.route("/products", methods=["POST"])
def create_product():
    try:
        product_controller.create_product(request)
        return jsonify(resp("OK", "Produto adicionado com sucesso.")), 201

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@products_bp.route("/products", methods=["GET"])
def get_products():
    try:
        products = product_controller.get_products()
        return jsonify(resp("OK", "Listagem obtida com sucesso.", products=products))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    try:
        product = product_controller.get_product_by_id(product_id)
        return jsonify(resp("OK", "Produto obtido com sucesso.", product=product))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@products_bp.route("/products/<int:product_id>", methods=["PATCH"])
def update_product(product_id):
    try:
        product_controller.update_product(request, product_id)
        return jsonify(resp("OK", "Produto alterado com sucesso."))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        product_controller.delete_product(product_id)
        return jsonify(resp("OK", "Produto deletado com sucesso."))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]