from flask import jsonify
from functools import wraps
from flask_login import current_user

from src.utils.ApiUtils import ApiUtils

resp = ApiUtils.response

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