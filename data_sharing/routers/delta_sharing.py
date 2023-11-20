from datetime import datetime
from typing import Any, Literal

import httpx
import orjson
from fastapi import APIRouter, Depends, Security
from fastapi.requests import Request
from fastapi.responses import Response
from pydantic import BaseModel

from data_sharing.permissions import header_scheme, is_authenticated
from data_sharing.schemas import delta_sharing
from data_sharing.settings import settings
from data_sharing.utils.qs import query_parametrize

router = APIRouter(
    tags=["delta_sharing"],
    dependencies=[Security(is_authenticated)],
)

sharing_client = httpx.AsyncClient(
    base_url=f"http://{settings.DELTA_SHARING_HOST}", timeout=30
)


async def forward_sharing_request(
    request: Request,
    response: Response,
    token: str,
    query: str = "",
    body: BaseModel = None,
    response_type: Literal["json", "text"] = "json",
    additional_headers: dict[str, str] = None,
) -> dict[str, Any] | str:
    additional_headers = additional_headers or {}
    url = httpx.URL(path=f"/sharing{request.url.path}", query=query.encode())
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={**additional_headers, "Authorization": f"Bearer {token}"},
        json=body.model_dump() if body else None,
    )
    sharing_res = await sharing_client.send(sharing_req)
    response.status_code = sharing_res.status_code
    return sharing_res.json() if response_type == "json" else sharing_res.text


@router.get(
    "/shares",
    response_model=delta_sharing.Pagination[delta_sharing.Share],
)
async def list_shares(
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    return await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
    )


@router.get(
    "/shares/{share_name}/schemas",
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
    return await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
    )


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
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
    return await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
    )


@router.get(
    "/shares/{share_name}/all-tables",
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
    return await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
    )


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
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
    return await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(startingTimestamp=startingTimestamp)),
    )


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
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
    sharing_res = await forward_sharing_request(
        request, response, token, response_type="text"
    )
    protocol, metadata = sharing_res.split()
    return {**orjson.loads(protocol), **orjson.loads(metadata)}


@router.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    response_model=delta_sharing.TableDataResponse,
)
async def query_table_data(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    body: delta_sharing.TableQueryRequest = None,
    token=Depends(header_scheme),
):
    sharing_res = await forward_sharing_request(
        request,
        response,
        token,
        body=body,
        response_type="text",
    )
    protocol, metadata, *files = sharing_res.split("\n")

    return {
        **orjson.loads(protocol),
        **orjson.loads(metadata),
        "files": [orjson.loads(file).get("file") for file in files if len(file) > 0],
    }
