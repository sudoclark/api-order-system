from src.errors.base_error import BaseHttpError

class BadRequestError(BaseHttpError):
    def __init__(self, message: str):
        super().__init__(type="Bad Request", status_code=400, message=message)
