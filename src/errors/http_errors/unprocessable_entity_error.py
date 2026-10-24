from src.errors.base_error import BaseHttpError

class UnprocessableEntityError(BaseHttpError):
    def __init__(self, message: str):
        super().__init__(type="Unprocessable Entity", status_code=422, message=message)