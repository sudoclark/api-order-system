from flask import Blueprint, request, jsonify

from utils.ApiUtils import ApiUtils
from src.errors.handle_error import handle_error
from src.controllers.user_controller import UserController
from src.models.mysql.settings.connect import db_manager_connection
from src.models.mysql.repositories.user_repository import UserRepository

user_repository = UserRepository(db_manager_connection)
user_controller = UserController(user_repository)

resp = ApiUtils.response

user_bp = Blueprint("user_routes_bp", __name__)

@user_bp.route("/users", methods=["POST"])
def create_user():
    try:
        user_controller.create_user(request)
        return jsonify(resp("OK", "Usuário criado com sucesso.")), 201
    
    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@user_bp.route("/users", methods=["GET"])
def get_users():
    try:
        users = user_controller.get_users()
        return jsonify(resp("OK", "Usuário obtido com sucesso", users=users))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        user = user_controller.get_user_by_id(user_id)
        return jsonify(resp("OK", "Usuário obtido com sucesso", user=user))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@user_bp.route("/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    try:
        user_controller.update_user(user_id, request)
        return jsonify(resp("OK", "Dados alterados com sucesso"))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user_controller.delete_user(user_id)
        return jsonify(resp("OK", "Usuário deletado com sucesso."))

    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"] 