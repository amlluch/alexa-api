from typing import Any
from functools import wraps

from alexa_api.errors import ApiError


def serverless(serverless_handler: Any) -> Any:
    def _inner(fn: Any) -> Any:
        @wraps(fn)
        def execute_serverless(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except ApiError as e:
                return {"statusCode": e.status_code, "body": '{"error": "' + str(e) + '"}'}
            except Exception as e:
                return {"statusCode": 500, "body": '{"error": "' + str(e) + '"}'}

        return execute_serverless

    if serverless_handler is None:
        return _inner

    return _inner(serverless_handler)
