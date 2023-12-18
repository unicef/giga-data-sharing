from fastapi.responses import PlainTextResponse

from data_sharing.schemas.delta_sharing import Error

other_common_responses = {
    400: {
        "model": Error,
        "description": "The request is malformed.",
    },
    401: {
        "content": {PlainTextResponse.media_type: {}},
        "description": (
            "The request is unauthenticated. The bearer token is missing or incorrect."
        ),
    },
    403: {
        "content": {PlainTextResponse.media_type: {}},
        "description": "The request is forbidden from being fulfilled.",
    },
    404: {
        "content": {PlainTextResponse.media_type: {}},
        "description": "The requested resource does not exist.",
    },
    500: {
        "model": Error,
        "description": "The request is not handled correctly due to a server error.",
    },
}
