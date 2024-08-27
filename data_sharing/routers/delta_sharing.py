from datetime import datetime
from typing import Annotated, Any, Literal, Optional

import httpx
from fastapi import APIRouter, Depends, Header, Path, Query, Security, status
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel, conint

from data_sharing.annotations.delta_sharing import (
    delta_sharing_capabilities_header_description,
    ending_timestamp_description,
    ending_version_description,
    include_historical_metadata_description,
    max_results_description,
    page_token_description,
    query_cdf_ndjson_description,
    query_data_ndjson_description,
    query_metadata_ndjson_description,
    schema_name_description,
    share_name_description,
    starting_timestamp_description,
    starting_version_description,
    table_name_description,
)
from data_sharing.annotations.responses import other_common_responses
from data_sharing.models import ApiKey
from data_sharing.permissions import HasTablePermissions, IsAuthenticated
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
    responses=other_common_responses,
)
async def list_shares(
    request: Request,
    response: Response,
    maxResults: Annotated[
        conint(ge=0), Query(description=max_results_description)
    ] = None,
    pageToken: Annotated[str, Query(description=page_token_description)] = None,
):
    query_params = {"maxResults": maxResults, "pageToken": pageToken}
    parametrized_query = query_parametrize(query_params)
    sharing_res, _ = await forward_sharing_request(
        request, response, parametrized_query
    )
    return sharing_res


@router.get(
    "/shares/{share_name}",
    response_model=delta_sharing.ShareData,
    responses=other_common_responses,
)
async def get_share(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[
        conint(ge=0), Query(description=max_results_description)
    ] = None,
    pageToken: Annotated[str, Query(description=page_token_description)] = None,
):
    query_params = {"maxResults": maxResults, "pageToken": pageToken}
    parametrized_query = query_parametrize(query_params)

    sharing_res, _ = await forward_sharing_request(
        request, response, parametrized_query
    )
    return sharing_res


@router.get(
    "/shares/{share_name}/schemas",
    response_model=delta_sharing.Pagination[delta_sharing.Schema],
    responses=other_common_responses,
)
async def list_schemas(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[
        conint(ge=0), Query(description=max_results_description)
    ] = None,
    pageToken: Annotated[str, Query(description=page_token_description)] = None,
):
    query_params = {"maxResults": maxResults, "pageToken": pageToken}
    parametrized_query = query_parametrize(query_params)

    sharing_res, _ = await forward_sharing_request(
        request, response, parametrized_query
    )
    return sharing_res


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
    responses=other_common_responses,
)
async def list_tables(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[
        conint(ge=0), Query(description=max_results_description)
    ] = None,
    pageToken: Annotated[str, Query(description=page_token_description)] = None,
    current_user: ApiKey = Depends(get_current_user),
):
    query_params = {"maxResults": maxResults, "pageToken": pageToken}
    parametrized_query = query_parametrize(query_params)
    sharing_res, error = await forward_sharing_request(
        request, response, parametrized_query
    )
    if error:
        return sharing_res

    role_codes = [r.id for r in current_user.roles]
    if "ADMIN" not in role_codes:
        sharing_res["items"] = list(
            filter(lambda s: s["name"] in role_codes, sharing_res["items"])
        )

    return sharing_res


@router.get(
    "/shares/{share_name}/all-tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
    responses=other_common_responses,
)
async def list_tables_in_share(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[
        conint(ge=0), Query(description=max_results_description)
    ] = None,
    pageToken: Annotated[str, Query(description=page_token_description)] = None,
    current_user: ApiKey = Depends(get_current_user),
):
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        query_parametrize({"maxResults": maxResults, "pageToken": pageToken}),
        response_type="full",
    )
    if error:
        return sharing_res

    sharing_json = sharing_res.json()
    role_codes = [r.id for r in current_user.roles]
    if "ADMIN" not in role_codes:
        sharing_json["items"] = list(
            filter(lambda s: s["name"] in role_codes, sharing_json["items"])
        )
    return sharing_json


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/version",
    dependencies=[Depends(HasTablePermissions.raises(True))],
    response_model=TableVersion,
    responses=other_common_responses,
)
async def query_table_version(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    table_name: Annotated[str, Path(description=table_name_description)],
    request: Request,
    response: Response,
    startingTimestamp: Annotated[
        datetime, Query(description=starting_timestamp_description)
    ] = None,
):
    sharing_res, _ = await forward_sharing_request(
        request,
        response,
        query_parametrize({"startingTimestamp": startingTimestamp}),
        response_type="full",
    )

    if (version := sharing_res.headers.get("delta-table-version")) is None:
        return ORJSONResponse(
            {
                "detail": f"Could not find version for table `{share_name}`.`{schema_name}`.`{table_name}`. Ensure that all parameters are spelled correctly."
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    response.headers["delta-table-version"] = version
    return sharing_res.headers


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
    dependencies=[Depends(HasTablePermissions.raises(True))],
    response_class=NDJSONResponse,
    response_description=query_metadata_ndjson_description,
    responses=other_common_responses,
)
async def query_table_metadata(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    table_name: Annotated[str, Path(description=table_name_description)],
    request: Request,
    response: Response,
    delta_sharing_capabilities: Annotated[
        str | None,
        Header(
            alias="delta-sharing-capabilities",
            description=delta_sharing_capabilities_header_description,
        ),
    ] = None,
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    sharing_res, error = await forward_sharing_request(
        request, response, response_type="full", additional_headers=additional_headers
    )
    if error:
        return sharing_res

    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )
    response.status_code = sharing_res.status_code
    return sharing_res.content


@router.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    dependencies=[Depends(HasTablePermissions.raises(True))],
    response_class=NDJSONResponse,
    response_description=query_data_ndjson_description,
    responses=other_common_responses,
)
async def query_table_data(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    table_name: Annotated[str, Path(description=table_name_description)],
    request: Request,
    response: Response,
    body: delta_sharing.TableQueryRequest = None,
    content_type: str | None = Header(None, alias="Content-Type"),
    delta_sharing_capabilities: Annotated[
        str | None,
        Header(
            alias="delta-sharing-capabilities",
            description=delta_sharing_capabilities_header_description,
        ),
    ] = None,
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    if content_type is not None:
        additional_headers["Content-Type"] = content_type

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        body=body,
        response_type="full",
        additional_headers=additional_headers,
    )
    if error:
        return sharing_res

    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )
    response.status_code = sharing_res.status_code
    return sharing_res.content


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/changes",
    dependencies=[Depends(HasTablePermissions.raises(True))],
    response_class=NDJSONResponse,
    response_description=query_cdf_ndjson_description,
    responses=other_common_responses,
)
async def query_table_change_data_feed(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    table_name: Annotated[str, Path(description=table_name_description)],
    request: Request,
    response: Response,
    delta_sharing_capabilities: Annotated[
        str | None,
        Header(
            alias="delta-sharing-capabilities",
            description=delta_sharing_capabilities_header_description,
        ),
    ] = None,
    startingVersion: Annotated[
        Optional[int], Query(description=starting_version_description)
    ] = 0,
    startingTimestamp: Annotated[
        Optional[str], Query(description=starting_timestamp_description)
    ] = None,
    endingVersion: Annotated[
        Optional[int], Query(description=ending_version_description)
    ] = None,
    endingTimestamp: Annotated[
        Optional[str], Query(description=ending_timestamp_description)
    ] = None,
    includeHistoricalMetadata: Annotated[
        Optional[bool], Query(description=include_historical_metadata_description)
    ] = None,
):
    additional_headers = {}
    if delta_sharing_capabilities is not None:
        additional_headers["delta-sharing-capabilities"] = delta_sharing_capabilities

    sharing_res, error = await forward_sharing_request(
        request,
        response,
        query_parametrize(
            {
                "startingVersion": startingVersion,
                "startingTimestamp": startingTimestamp,
                "endingVersion": endingVersion,
                "endingTimestamp": endingTimestamp,
                "includeHistoricalMetadata": includeHistoricalMetadata,
            },
        ),
        response_type="full",
        additional_headers=additional_headers,
    )
    if error:
        return sharing_res

    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )
    response.status_code = sharing_res.status_code
    return sharing_res.content
