from .base_error import BaseHttpError

def handle_error(error: Exception) -> dict:
    if isinstance(error, BaseHttpError):
        return {
            "status_code": error.status_code,
            "data": {
                "type": error.type,
                "message": error.message
            }
        }

    return {
        "status_code": 500,
        "data": {
            "type": "Server Error",
            "message": str(error)
        }
    }