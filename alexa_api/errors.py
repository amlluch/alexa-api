class ApiError(RuntimeError):
    status_code = 500


class AlexaRepositoryError(ApiError):
    status_code = 417
