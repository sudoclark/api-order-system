from src.errors.base_error import BaseHttpError

class NotFoundError(BaseHttpError):
    def __init__(self, message: str):
        super().__init__(type="Not Found", status_code=404, message=message)