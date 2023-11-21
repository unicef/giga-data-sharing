from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from data_sharing.constants import __version__
from data_sharing.permissions import header_scheme
from data_sharing.routers import delta_sharing
from data_sharing.schemas.delta_sharing import ProfileFile
from data_sharing.settings import settings

app = FastAPI(
    title="Giga Data Sharing",
    version=__version__,
    docs_url="/",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("", tags=["core"])
async def health_check():
    return {"status": "ok"}


@app.get("/profileFile", response_model=ProfileFile, tags=["core"])
async def profile_file(
    token=Depends(header_scheme),
):
    TEMP_CREDENTIALS_VERSION = 1
    TEMP_EXPIRATION_TIME = "2029-10-10T10:10:10.000Z"

    return {
        "shareCredentialsVersion": TEMP_CREDENTIALS_VERSION,
        "endpoint": (
            f"{settings.DELTA_SHARING_HOST}/sharing"
            if settings.PYTHON_ENV == "production"
            else "http://localhost:5000"
        ),
        "bearerToken": token,
        "expirationTimestamp": TEMP_EXPIRATION_TIME,
    }


app.include_router(delta_sharing.router)
