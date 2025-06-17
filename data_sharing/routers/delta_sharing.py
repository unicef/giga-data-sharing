from datetime import datetime
from typing import Any, Literal, Optional

import httpx
from fastapi import APIRouter, Depends, Header, Security, status
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel

from data_sharing.annotations.responses import other_common_responses
from data_sharing.models import ApiKey
from data_sharing.permissions import HasTablePermissions, IsAuthenticated
from data_sharing.permissions.access_control import (
    filter_schemas_by_access,
    filter_tables_by_access,
)
from data_sharing.permissions.utils import get_current_user
from data_sharing.schemas import delta_sharing
from data_sharing.schemas.delta_sharing import TableVersion
from data_sharing.settings import settings
from data_sharing.utils.qs import query_parametrize
from data_sharing.utils.responses import NDJSONResponse

router = APIRouter(
    tags=["delta_sharing"],
    dependencies=[Security(IsAuthenticated.raises(True))],
)

sharing_client = httpx.AsyncClient(
    base_url=f"http://{settings.DELTA_SHARING_HOST}", timeout=300
)


async def forward_sharing_request(
    request: Request,
    response: Response,
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
        headers={
            **additional_headers,
            "Authorization": f"Bearer {settings.DELTA_BEARER_TOKEN}",
        },
        json=body.model_dump() if body else None,
    )
    sharing_res = await sharing_client.send(sharing_req)
    if sharing_res.is_error:
        json_content = sharing_res.json()
        return ORJSONResponse(json_content, status_code=sharing_res.status_code), True

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
    responses=other_common_responses,
)
async def list_shares(
    request: Request, response: Response, maxResults: int = None, pageToken: str = None
):
    query = query_parametrize({"maxResults": maxResults, "pageToken": pageToken})
    res, error = await forward_sharing_request(request, response, query)
    if error:
        return res
    return res


@router.get(
    "/shares/{share_name}",
    response_model=delta_sharing.ShareData,
    responses=other_common_responses,
)
async def get_share(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
):
    query = query_parametrize({"maxResults": maxResults, "pageToken": pageToken})
    res, error = await forward_sharing_request(request, response, query)
    if error:
        return res
    return res


@router.get(
    "/shares/{share_name}/schemas",
    response_model=delta_sharing.Pagination[delta_sharing.Schema],
    responses=other_common_responses,
)
async def list_schemas(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    current_user: ApiKey = Depends(get_current_user),
):
    query = query_parametrize({"maxResults": maxResults, "pageToken": pageToken})
    res, error = await forward_sharing_request(request, response, query)
    if error:
        return res
    res["items"] = filter_schemas_by_access(res["items"], current_user)
    return res


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
    responses=other_common_responses,
)
async def list_tables(
    share_name: str,
    schema_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    current_user: ApiKey = Depends(get_current_user),
):
    query = query_parametrize({"maxResults": maxResults, "pageToken": pageToken})
    res, error = await forward_sharing_request(request, response, query)
    if error:
        return res
    res["items"] = filter_tables_by_access(schema_name, res["items"], current_user)
    return res


from collections import defaultdict


@router.get(
    "/shares/{share_name}/all-tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
    responses=other_common_responses,
)
async def list_all_tables(
    share_name: str,
    request: Request,
    response: Response,
    maxResults: int = None,
    pageToken: str = None,
    current_user: ApiKey = Depends(get_current_user),
):
    query = query_parametrize({"maxResults": maxResults, "pageToken": pageToken})
    res, error = await forward_sharing_request(
        request, response, query, response_type="full"
    )
    if error:
        return res

    res_json = res.json()
    role_ids = [r.id for r in current_user.roles]

    if "ADMIN" in role_ids:
        return res_json

    # 🔧 FIXED: Use correct key 'schema' instead of 'schemaName'
    schema_map = defaultdict(list)
    for t in res_json.get("items", []):
        schema = t.get("schema")  # <- previously: schemaName
        if schema:
            schema_map[schema].append(t)

    filtered = []
    for schema, tables in schema_map.items():
        filtered.extend(filter_tables_by_access(schema, tables, current_user))

    res_json["items"] = filtered
    return res_json


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
    response_model=TableVersion,
    responses=other_common_responses,
    dependencies=[Depends(HasTablePermissions.raises(True))],
)
async def query_table_version(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    startingTimestamp: Optional[datetime] = None,
):
    # ❌ Don't allow 'None' in query
    params = {}
    if startingTimestamp:
        params["startingTimestamp"] = startingTimestamp.isoformat()

    query = query_parametrize(params)

    # 🔁 Forward request
    res, _ = await forward_sharing_request(
        request, response, query=query, response_type="full"
    )

    version = res.headers.get("delta-table-version")
    if version is None:
        return ORJSONResponse(
            {"detail": f"Could not find version for `{table_name}`."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    response.headers["delta-table-version"] = version
    return {"version": version}


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
    response_class=NDJSONResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
)
async def query_table_metadata(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    delta_sharing_capabilities: str = Header(None, alias="delta-sharing-capabilities"),
):
    headers = (
        {"delta-sharing-capabilities": delta_sharing_capabilities}
        if delta_sharing_capabilities
        else {}
    )
    res, error = await forward_sharing_request(
        request, response, response_type="full", additional_headers=headers
    )
    if error:
        return res
    response.headers["delta-table-version"] = res.headers.get("delta-table-version")
    return res.content


@router.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    response_class=NDJSONResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
)
async def query_table_data(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    body: delta_sharing.TableQueryRequest = None,
    content_type: str = Header(None, alias="Content-Type"),
    delta_sharing_capabilities: str = Header(None, alias="delta-sharing-capabilities"),
):
    headers = {}
    if delta_sharing_capabilities:
        headers["delta-sharing-capabilities"] = delta_sharing_capabilities
    if content_type:
        headers["Content-Type"] = content_type

    res, error = await forward_sharing_request(
        request, response, body=body, response_type="full", additional_headers=headers
    )
    if error:
        return res
    response.headers["delta-table-version"] = res.headers.get("delta-table-version")
    return res.content


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/changes",
    response_class=NDJSONResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
)
async def query_table_changes(
    share_name: str,
    schema_name: str,
    table_name: str,
    request: Request,
    response: Response,
    startingVersion: int = None,
    endingVersion: int = None,
    startingTimestamp: str = None,
    endingTimestamp: str = None,
    includeHistoricalMetadata: bool = None,
    delta_sharing_capabilities: str = Header(None, alias="delta-sharing-capabilities"),
):
    headers = (
        {"delta-sharing-capabilities": delta_sharing_capabilities}
        if delta_sharing_capabilities
        else {}
    )
    query = query_parametrize(
        {
            "startingVersion": startingVersion,
            "endingVersion": endingVersion,
            "startingTimestamp": startingTimestamp,
            "endingTimestamp": endingTimestamp,
            "includeHistoricalMetadata": includeHistoricalMetadata,
        }
    )
    res, error = await forward_sharing_request(
        request, response, query=query, response_type="full", additional_headers=headers
    )
    if error:
        return res
    response.headers["delta-table-version"] = res.headers.get("delta-table-version")
    return res.content
