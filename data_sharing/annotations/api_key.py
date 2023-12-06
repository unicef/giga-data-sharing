class ApiKeyDescriptions:
    description = "Describe what this API key will be used for or who will use it"
    validity = (
        "Validity of the API key in days. Set to 0 for no expiration (not recommended)"
    )
    roles = (
        "List of countries, using the ISO-3166 alpha-3 code, to grant access to. Refer"
        " to the `/roles` route to get a list of available roles."
    )
