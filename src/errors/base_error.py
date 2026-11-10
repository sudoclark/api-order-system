class BaseHttpError(Exception):
    def __init__(self, type: str, status_code: int, message: str):
        super().__init__(message)
        self.type = type
        self.status_code = status_code
        self.message = message
