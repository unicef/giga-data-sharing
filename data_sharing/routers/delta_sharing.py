from datetime import datetime
from typing import Annotated, Any, Literal, Optional

import httpx
import orjson
from fastapi import APIRouter, Depends, Header, Path, Query, Security
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel

from data_sharing.annotations.delta_sharing import (
    delta_sharing_capabilities_header_description,
    ending_timestamp_description,
    ending_version_description,
    include_historical_metadata_description,
    max_results_description,
    page_token_description,
    schema_name_description,
    share_name_description,
    starting_timestamp_description,
    starting_version_description,
    table_name_description,
)
from data_sharing.models import ApiKey
from data_sharing.permissions import HasTablePermissions, IsAuthenticated
from data_sharing.permissions.utils import get_current_user
from data_sharing.schemas import delta, delta_sharing
from data_sharing.settings import settings
from data_sharing.utils.qs import query_parametrize

router = APIRouter(
    tags=["delta_sharing"],
    dependencies=[Security(IsAuthenticated.raises(True))],
)

sharing_client = httpx.AsyncClient(
    base_url=f"http://{settings.DELTA_SHARING_HOST}", timeout=30
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
)
async def list_shares(
    request: Request,
    response: Response,
    maxResults: Annotated[int, Query(description=(max_results_description))] = None,
    pageToken: Annotated[int, Query(description=(page_token_description))] = None,
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)
    sharing_res, error = await forward_sharing_request(
        request, response, parametrized_query, response_type="full"
    )
    return sharing_res.json()


@router.get(
    "/shares/{share_name}",
    response_model=delta_sharing.ShareData,
)
async def get_share(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[int, Query(description=(max_results_description))] = None,
    pageToken: Annotated[int, Query(description=(page_token_description))] = None,
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)

    sharing_res, error = await forward_sharing_request(
        request, response, parametrized_query
    )
    return sharing_res


@router.get(
    "/shares/{share_name}/schemas",
    response_model=delta_sharing.Pagination[delta_sharing.Schema],
)
async def list_schemas(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[int, Query(description=max_results_description)] = None,
    pageToken: Annotated[int, Query(description=page_token_description)] = None,
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
    parametrized_query = query_parametrize(query_params)

    sharing_res, error = await forward_sharing_request(
        request, response, parametrized_query
    )
    return sharing_res


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables",
    response_model=delta_sharing.Pagination[delta_sharing.Table],
)
async def list_tables(
    share_name: Annotated[str, Path(description=share_name_description)],
    schema_name: Annotated[str, Path(description=schema_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[int, Query(description=max_results_description)] = None,
    pageToken: Annotated[int, Query(description=page_token_description)] = None,
    current_user: ApiKey = Depends(get_current_user),
):
    query_params = dict(maxResults=maxResults, pageToken=pageToken)
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
)
async def list_tables_in_share(
    share_name: Annotated[str, Path(description=share_name_description)],
    request: Request,
    response: Response,
    maxResults: Annotated[int, Query(description=max_results_description)] = None,
    pageToken: Annotated[int, Query(description=page_token_description)] = None,
    current_user: ApiKey = Depends(get_current_user),
):
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        query_parametrize(dict(maxResults=maxResults, pageToken=pageToken)),
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
    sharing_res, error = await forward_sharing_request(
        request,
        response,
        query_parametrize(dict(startingTimestamp=startingTimestamp)),
        response_type="full",
    )
    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )

    return None


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/metadata",
    response_model=delta_sharing.TableMetadataResponse | delta.TableMetadataResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
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

    res_split = [s for s in sharing_res.text.split("\n") if s != ""]

    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )

    if len(res_split) == 1:
        return ORJSONResponse(sharing_res.json(), status_code=sharing_res.status_code)
    else:
        protocol, metadata = res_split
        return {**orjson.loads(protocol), **orjson.loads(metadata)}


@router.post(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/query",
    response_model=delta_sharing.TableDataResponse | delta.TableDataResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
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

    res_split = [s for s in sharing_res.text.split("\n") if s != ""]
    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )
    if len(res_split) == 2:
        protocol, metadata = res_split
        return {
            **orjson.loads(protocol),
            **orjson.loads(metadata),
            "files": [],
        }

    else:
        protocol, metadata, *files = res_split
        non_empty_files = [
            orjson.loads(file).get("file") for file in files if len(file) > 0
        ]

        return {
            **orjson.loads(protocol),
            **orjson.loads(metadata),
            "files": non_empty_files,
        }


@router.get(
    "/shares/{share_name}/schemas/{schema_name}/tables/{table_name}/changes",
    response_model=delta_sharing.TableDataChangeResponse
    | delta.TableDataChangeResponse,
    dependencies=[Depends(HasTablePermissions.raises(True))],
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
    ] = None,
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
    response.headers["delta-table-version"] = sharing_res.headers.get(
        "delta-table-version"
    )
    if len(res_split) == 1:
        json_content = sharing_res.json()
        status_code = sharing_res.status_code
        return ORJSONResponse(json_content, status_code=status_code)
    else:
        protocol, metadata, *remaining_items = res_split
        change_data_feed = [orjson.loads(item) for item in remaining_items]
        merged_dict = {
            **orjson.loads(protocol),
            **orjson.loads(metadata),
            "files": change_data_feed,
        }
        return merged_dict
