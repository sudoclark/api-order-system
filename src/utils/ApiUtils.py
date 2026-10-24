class ApiUtils:

    @staticmethod
    def response(status, message, **kwargs):
        response = {"status": status, "message": message}

        response.update(**kwargs)

        return response