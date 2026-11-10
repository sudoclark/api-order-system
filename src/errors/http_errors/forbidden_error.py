from src.errors.base_error import BaseHttpError

class ForbiddenError(BaseHttpError):
    def __init__(self, message: str):
        super().__init__(type="Forbidden", status_code=403, message=message)