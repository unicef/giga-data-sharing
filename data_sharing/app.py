from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from data_sharing.constants import __version__
from data_sharing.routers import delta_sharing
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


app.include_router(delta_sharing.router)
