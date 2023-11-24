from datetime import datetime
from typing import Any, Literal, Optional, Union
import httpx
import orjson
from fastapi import APIRouter, Depends, Header, Security
from fastapi.requests import Request
from fastapi.responses import JSONResponse, ORJSONResponse, Response
from pydantic import BaseModel

from data_sharing.permissions import header_scheme, is_authenticated
from data_sharing.schemas import delta_sharing, delta
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
    response_type: Literal["json", "text", "full"] = "json",
    additional_headers: dict[str, str] = None,
) -> tuple[dict[str, Any] | str | httpx.Response | Response, bool]:
    additional_headers = additional_headers or {}
    url = httpx.URL(path=f"/sharing{request.url.path}", query=query.encode())
    sharing_req = sharing_client.build_request(
        url=url,
        method=request.method,
        headers={**additional_headers, "Authorization": f"Bearer {token}"},
        json=body.model_dump() if body else None,
    )
    sharing_res = await sharing_client.send(sharing_req)
    if sharing_res.is_error:
        json_content = sharing_res.json()
        status_code = sharing_res.status_code
        return (
            ORJSONResponse(json_content, status_code=status_code),
            True,
        )

    response.status_code = sharing_res.status_code
    match response_type:
        case "json":
            return sharing_res.json(), False
        case "text":
            return sharing_res.text, False
        case "full":
            return sharing_res, False
        case _:
            raise ValueError(f"Unknown {response_type=}")


@router.get(
    "/shares",
    response_model=delta_sharing.Pagination[delta_sharing.Share],
)
async def list_shares(
    request: Request,
    response: Response,
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    token=Depends(header_scheme),
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        parametrized_query,
    )
    headers = {"Content-Type": "application/json; charset=utf-8"}
    return JSONResponse(content=sharing_res, headers=headers)


@router.get(
    "/shares/{share_name}",
    response_model=delta_sharing.ShareData,
)
async def get_share(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    token=Depends(header_scheme),
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        parametrized_query,
    )

    headers = {"Content-Type": "application/json; charset=utf-8"}
    return JSONResponse(content=sharing_res, headers=headers)


@router.get(
    "/shares/{share_name}/schemas",
    response_model=delta_sharing.Pagination[delta_sharing.Schema],
)
async def list_schemas(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    token=Depends(header_scheme),
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        parametrized_query,
    )
    headers = {"Content-Type": "application/json; charset=utf-8"}
    return JSONResponse(content=sharing_res, headers=headers)


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
)
async def list_tables(
    share_name: str,
    schema_name: str,
    request: Request,
    response: Response,
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    token=Depends(header_scheme),
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        parametrized_query,
    )
    headers = {"Content-Type": "application/json; charset=utf-8"}
    return JSONResponse(content=sharing_res, headers=headers)


@router.get(
    "/shares/{share}/all-tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
)
async def list_tables_in_share(
    share: str,
    request: Request,
    response: Response,
    maxResults: Optional[int] = None,
    pageToken: Optional[str] = None,
    token=Depends(header_scheme),
):
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
        response_type="full",
    )
    headers = {"Content-Type": "application/json; charset=utf-8"}
    sharing_res_json = JSONResponse(content=sharing_res.json(), headers=headers)
    return sharing_res if error else sharing_res_json


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
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
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(dict(startingTimestamp=startingTimestamp)),
        response_type="full",
    )

    return sharing_res if error else Response(headers=sharing_res.headers, content=None)


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
    response_model=Union[
        delta_sharing.TableDataChangeResponse, delta.TableMetadataResponse
    ],
)
async def query_table_metadata(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    token=Depends(header_scheme),
    delta_sharing_capabilities: str
    | None = Header(None, alias="delta-sharing-capabilities"),
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        response_type="full",
        additional_headers=additional_headers,
    )
    if error:
        return sharing_res

    res_split = [s for s in sharing_res.text.split("\n") if s != ""]
    headers = sharing_res.headers
    if len(res_split) == 1:
        json_content = sharing_res.json()
        status_code = sharing_res.status_code
        return ORJSONResponse(json_content, status_code=status_code, headers=headers)
    else:
        protocol, metadata = res_split
        merged_dict = {**orjson.loads(protocol), **orjson.loads(metadata)}
        return JSONResponse(content=merged_dict, headers=headers)


@router.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    response_model=Union[delta_sharing.TableDataResponse, delta.TableDataResponse],
)
async def query_table_data(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    body: delta_sharing.TableQueryRequest = None,
    token=Depends(header_scheme),
    content_type: str | None = Header(None, alias="Content-Type"),
    delta_sharing_capabilities: str
    | None = Header(None, alias="delta-sharing-capabilities"),
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    if content_type is not None:
        additional_headers["Content-Type"] = content_type

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        body=body,
        response_type="full",
        additional_headers=additional_headers,
    )
    if error:
        return sharing_res

    res_split = [s for s in sharing_res.text.split("\n") if s != ""]
    headers = sharing_res.headers

    if len(res_split) == 2:
        protocol, metadata = res_split
        merged_dict = {**orjson.loads(protocol), **orjson.loads(metadata), "files": []}
        return JSONResponse(content=merged_dict, headers=headers)

    else:
        protocol, metadata, *files = res_split
        non_empty_files = [
            orjson.loads(file).get("file") for file in files if len(file) > 0
        ]
        merged_dict = {
            **orjson.loads(protocol),
            **orjson.loads(metadata),
            "files": non_empty_files,
        }
        return JSONResponse(content=merged_dict, headers=headers)


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/changes",
    response_model=Union[
        delta_sharing.TableDataChangeResponse, delta.TableDataChangeResponse
    ],
)
async def query_table_change_data_feed(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    token=Depends(header_scheme),
    delta_sharing_capabilities: str
    | None = Header(None, alias="delta-sharing-capabilities"),
    startingVersion: Optional[int] = None,
    startingTimestamp: Optional[str] = None,
    endingVersion: Optional[int] = None,
    endingTimestamp: Optional[str] = None,
    includeHistoricalMetadata: Optional[bool] = None,
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        token,
        query_parametrize(
            dict(
                startingVersion=startingVersion,
                startingTimestamp=startingTimestamp,
                endingVersion=endingVersion,
                endingTimestamp=endingTimestamp,
                includeHistoricalMetadata=includeHistoricalMetadata,
            ),
        ),
        response_type="full",
        additional_headers=additional_headers,
    )
    if error:
        return sharing_res

    res_split = [s for s in sharing_res.text.split("\n") if s != ""]
    headers = sharing_res.headers
    if len(res_split) == 1:
        json_content = sharing_res.json()
        status_code = sharing_res.status_code
        return ORJSONResponse(json_content, status_code=status_code, headers=headers)
    else:
        protocol, metadata = res_split
        merged_dict = {**orjson.loads(protocol), **orjson.loads(metadata)}
        return JSONResponse(content=merged_dict, headers=headers)
