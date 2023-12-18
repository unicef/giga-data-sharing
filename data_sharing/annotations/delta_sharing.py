delta_sharing_capabilities_header_description = (
    "Indicates the format to expect. Two Values are supported:"
    " `responseFormat=parquet` Represents the format of the delta sharing protocol"
    " that has been used in delta-sharing-spark 1.0 and less, and is also the default"
    " format if `responseFormat` is missing from the header. `responseFormat=delta` "
    " format can be used to read a shared delta table with minReaderVersion > 1, which"
    " contains readerFeatures such as Deletion Vector or Column Mapping."
    "`readerfeatures` is only useful when `responseformat=delta`"
)

ending_version_description = "The ending version of the query, inclusive."

ending_timestamp_description = (
    "The ending timestamp of the query, a string in the [Timestamp"
    " Format](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#timestamp-format),"
    " which will be converted to a version created less than or equal to this"
    " timestamp."
)

include_historical_metadata_description = (
    "If set to true, return the historical metadata if seen in the delta log. This is"
    " for the streaming client to check if the table schema is still read compatible."
)

max_results_description = (
    "The maximum number of results per page that should be returned. If the number of"
    " available results is larger than `maxResults`, the response will provide a"
    " `nextPageToken` that can be used to get the next page of results in subsequent"
    " list requests. The server may return fewer than `maxResults` items even if there"
    " are more available. The client should check `nextPageToken` in the response to"
    " determine if there are more available. Must be non-negative. 0 will return no"
    " results but `nextPageToken` may be populated."
)

page_token_description = (
    "Specifies a page token to use. Set `pageToken` to the `nextPageToken` returned by"
    " a previous list request to get the next page of results. `nextPageToken` will not"
    " be returned in a response if there are no more results available."
)


schema_name_description = "The schema name to query. It's case-insensitive."

share_name_description = "The share name to query. It's case-insensitive."

starting_timestamp_description = (
    "The starting timestamp of the query, a string in the [Timestamp"
    " Format](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#timestamp-format),"
    " which will be converted to a version created greater or equal to this timestamp."
)

starting_version_description = "The starting version of the query, inclusive."

table_name_description = "The table name to query. It's case-insensitive."

table_version_description = "A value which represents the current table version."

query_metadata_ndjson_description = """
A sequence of JSON strings delimited by newline. Each line is a JSON object defined in
[API Response Format in Parquet](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-parquet).
The response contains two lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) object.

When `responseFormat=delta`, each line is a JSON object defined in
[API Response Format in Delta](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-delta).
The response contains two lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol-in-delta-format) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata-in-delta-format) object.
"""

query_data_ndjson_description = """
A sequence of JSON strings delimited by newline. Each line is a JSON object defined in
[API Response Format in Parquet](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-parquet).
The response contains multiple lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) object.
- The rest of the lines are [JSON wrapper objects](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) for [data change files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#data-change-files), [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata), or [files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#file).
  - The lines are [data change files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#data-change-files) with possible historical [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) (when `startingVersion` is set).
  - The lines are [files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#file) in the table (otherwise).
  - The ordering of the lines doesn't matter.

When `responseFormat=delta`, each line is a JSON object defined in
[API Response Format in Delta](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-delta).
The response contains multiple lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol-in-delta-format) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata-in-delta-format) object.
- The rest of the lines are [JSON wrapper objects](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) for [data change files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#data-change-files), [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata-in-delta-format), or [files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#file-in-delta-format).
  - The lines are [files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#file-in-delta-format) which wraps the delta single action in the table (otherwise), with possible historical [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata-in-delta-format) (when `startingVersion` is set).
  - The ordering of the lines doesn't matter.
"""

query_cdf_ndjson_description = """
A sequence of JSON strings delimited by newline. Each line is a JSON object defined in
[API Response Format in Parquet](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-parquet).
The response contains multiple lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) object.
- The rest of the lines are [JSON wrapper objects](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line) for [Data Change Files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#data-change-files) of the change data feed.
  - Historical [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) will be returned if `includeHistoricalMetadata` is set to true.
  - The ordering of the lines doesn't matter.

When `responseFormat=delta`, each line is a JSON object defined in
[API Response Format in Delta](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#api-response-format-in-delta).
The response contains multiple lines:
- The first line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Protocol](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#protocol-in-delta-format) object.
- The second line is a [JSON wrapper object](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) containing the table [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata-in-delta-format) object.
- The rest of the lines are [JSON wrapper objects](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#json-wrapper-object-in-each-line-in-delta) for [Files](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#file-in-delta-format) of the change data feed.
  - Historical [Metadata](https://github.com/delta-io/delta-sharing/blob/main/PROTOCOL.md#metadata) will be returned if `includeHistoricalMetadata` is set to true.
  - The ordering of the lines doesn't matter.
"""


class ProfileFileDescriptions:
    share_credentials_version = (
        "The file format version of the profile file. This version will be increased"
        " whenever non-forward-compatible changes are made to the profile format. When"
        " a client is running an unsupported profile file format version, it should"
        " show an error message instructing the user to upgrade to a newer version of"
        " their client."
    )
    endpoint = "The url of the sharing server."
    bearer_token = "The bearer token to access the server."
    expiration_time = (
        "The expiration time of the bearer token in [ISO"
        " 8601](https://www.w3.org/TR/NOTE-datetime) format. This field is optional and"
        " if it is not provided, the bearer token can be seen as never expire."
    )
