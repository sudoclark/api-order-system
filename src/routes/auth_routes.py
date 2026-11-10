from flask import Blueprint, request, jsonify
from flask_login import login_required

from src.utils.ApiUtils import ApiUtils
from src.errors.handle_error import handle_error
from src.controllers.auth_controller import AuthController
from src.models.mysql.settings.connect import db_manager_connection
from src.models.mysql.repositories.auth_repository import AuthRepository

auth_bp = Blueprint("auth_routes_bp", __name__)
resp = ApiUtils.response

auth_repository = AuthRepository(db_manager_connection)
auth_controller = AuthController(auth_repository)

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        auth_controller.login(request)
        return jsonify(resp("OK", "Usuário autenticado com sucesso"))
    
    except Exception as ex:
        error = handle_error(ex)
        return jsonify(error["data"]), error["status_code"]

@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    auth_controller.logout()
    return jsonify(resp("OK", "Usuário deslogado com sucesso."))
