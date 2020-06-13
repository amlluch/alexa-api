class ApiError(RuntimeError):
    status_code = 500


class AlexaRepositoryError(ApiError):
    status_code = 417


class AWSError(ApiError):
    status_code = 500


class RepositoryError(ApiError):
    status_code = 417


class RecordNotFound(ApiError):
    status_code = 404


class RecordExists(ApiError):
    status_code = 409
