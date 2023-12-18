from fastapi.responses import Response


class NDJSONResponse(Response):
    media_type = "application/x-ndjson"
