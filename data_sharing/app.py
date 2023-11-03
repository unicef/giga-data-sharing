from datetime import datetime

import httpx
import orjson
from fastapi import Depends, FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, Response

from data_sharing.constants import __version__
from data_sharing.permissions import header_scheme, is_authenticated
from data_sharing.schemas import delta_sharing
from data_sharing.settings import settings

app = FastAPI(
    title="Giga Data Sharing",
    version=__version__,
    docs_url="/docs",
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

sharing_client = httpx.AsyncClient(base_url="http://sharing-server:8890", timeout=30)


@app.get("", tags=["core"])
async def health_check():
    return {"status": "ok"}


@app.get(
    "/shares",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.Pagination[delta_sharing.Share],
)
async def list_shares(
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    url = httpx.URL(path="/sharing/shares", query=request.url.query.encode())
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json()


@app.get(
    "/shares/{share_name}",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.Share,
)
async def get_share(
    share_name: str,
    request: Request,
    response: Response,
    token=Depends(header_scheme),
):
    url = httpx.URL(path=f"/sharing/shares/{share_name}")
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json()


@app.get(
    "/shares/{share_name}/schemas",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.Pagination[delta_sharing.Schema],
)
async def list_schemas(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/schemas", query=request.url.query.encode()
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json()


@app.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.Pagination[delta_sharing.Table],
)
async def list_tables(
    share_name: str,
    schema_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/schemas/{schema_name}/tables",
        query=request.url.query.encode(),
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json()


@app.get(
    "/shares/{share_name}/all-tables",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.Pagination[delta_sharing.Table],
)
async def list_tables_in_share(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/all-tables",
        query=request.url.query.encode(),
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json()


@app.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.TableVersion,
)
async def query_table_version(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    startingTimestamp: datetime = None,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
        query=request.url.query.encode(),
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.headers


@app.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.TableMetadataResponse,
)
async def query_table_metadata(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata"
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    protocol, metadata = sharing_res.text.split()
    return {**orjson.loads(protocol), **orjson.loads(metadata)}


@app.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
    response_model=delta_sharing.TableDataResponse,
)
async def query_table_data(
    share_name: str,
    schema_name: str,
    table_name: str,
    body: delta_sharing.TableQueryRequest,
    request: Request,
    response: Response,
    token=Depends(header_scheme),
):
    url = httpx.URL(
        path=f"/sharing/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query"
    )
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={"Authorization": f"Bearer {token}"},
        json=body.model_dump(),
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    protocol, metadata, *files = sharing_res.text.split()
    return {
        **orjson.loads(protocol),
        **orjson.loads(metadata),
        "files": [orjson.loads(file) for file in files],
    }
