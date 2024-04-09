from socket import gethostname

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from data_sharing.constants import __version__
from data_sharing.routers import api_key, delta_sharing, role
from data_sharing.settings import settings

if settings.SENTRY_DSN and settings.IN_PRODUCTION:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        sample_rate=1.0,
        enable_tracing=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=settings.DEPLOY_ENV,
        release=f"github.com/unicef/giga-data-sharing:{settings.COMMIT_SHA}",
        server_name=f"data-sharing-proxy-{settings.DEPLOY_ENV}@{gethostname()}",
    )

app = FastAPI(
    title="Giga Data Sharing",
    description=(
        "The Data Sharing API is a lightweight custom proxy"
        " layer written with FastAPI on top of the Delta Sharing reference server."
        " The proxy layer implements token-based access control, "
        "and API documentation using Swagger UI."
        "For feedback or issues, visit our "
        "[GitHub Issues page](https://github.com/unicef/giga-data-sharing/issues)."
    ),
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


@app.get("/health", tags=["core"])
async def health_check():
    return {"status": "ok"}


app.include_router(delta_sharing.router)
app.include_router(role.router)
app.include_router(api_key.router)
