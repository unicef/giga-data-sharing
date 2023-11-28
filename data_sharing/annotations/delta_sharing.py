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

share_name_description = "The share name to query. It's case-insensitive."
