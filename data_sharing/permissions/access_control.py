import logging

# Set up logger
logger = logging.getLogger("data_sharing.access")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Mapping of short role codes to schema names
ROLE_TO_SCHEMA = {
    "SCHM": "school-master",
    "QOS": "qos",
    "REF": "school-reference",
    "GERR": "school-geolocation-error",
}


def parse_user_roles(roles: list[str]):
    known_schemas = set(ROLE_TO_SCHEMA.keys())
    schema_roles = {ROLE_TO_SCHEMA[r] for r in roles if r in known_schemas}
    country_roles = {r for r in roles if r not in known_schemas and r != "ADMIN"}

    logger.debug(f"[parse_user_roles] Input roles: {roles}")
    logger.debug(
        f"[parse_user_roles] Parsed schema_roles: {schema_roles}, country_roles: {country_roles}"
    )

    return schema_roles, country_roles


def filter_schemas_by_access(schemas: list[dict], user) -> list[dict]:
    role_ids = [r.id for r in user.roles]
    schema_roles, _ = parse_user_roles(role_ids)

    if "ADMIN" in role_ids:
        logger.debug("[filter_schemas_by_access] ADMIN access granted to all schemas.")
        return schemas

    allowed = [s for s in schemas if s["name"] in schema_roles]
    logger.debug(
        f"[filter_schemas_by_access] Allowed schemas: {[s['name'] for s in allowed]}"
    )
    return allowed


def filter_tables_by_access(schema_name: str, tables: list[dict], user) -> list[dict]:
    role_ids = [r.id for r in user.roles]
    schema_roles, country_roles = parse_user_roles(role_ids)

    if "ADMIN" in role_ids:
        logger.debug("[filter_tables_by_access] ADMIN access granted to all tables.")
        return tables

    if schema_roles and schema_name not in schema_roles:
        logger.debug(
            f"[filter_tables_by_access] Schema '{schema_name}' is not in user's schema roles."
        )
        return []

    if not country_roles:
        logger.debug(
            f"[filter_tables_by_access] No country restrictions. All tables in schema '{schema_name}' allowed."
        )
        return tables

    filtered = [t for t in tables if t["name"].split("_", 1)[0] in country_roles]
    logger.debug(
        f"[filter_tables_by_access] Allowed tables for schema '{schema_name}': {[t['name'] for t in filtered]}"
    )
    return filtered


def user_has_access_to_table(user, schema_name: str, table_name: str) -> bool:
    role_ids = [r.id for r in user.roles]
    schema_roles, country_roles = parse_user_roles(role_ids)

    if "ADMIN" in role_ids:
        logger.debug(
            f"[user_has_access_to_table] ADMIN access granted to {schema_name}.{table_name}"
        )
        return True

    if schema_roles and schema_name not in schema_roles:
        logger.debug(
            f"[user_has_access_to_table] Access denied: {schema_name} not in schema roles."
        )
        return False

    if not country_roles:
        logger.debug(
            f"[user_has_access_to_table] No country roles; access granted to {table_name}."
        )
        return True

    country_prefix = table_name.split("_", 1)[0]
    has_access = country_prefix in country_roles
    logger.debug(
        f"[user_has_access_to_table] Access {'granted' if has_access else 'denied'} to {table_name}."
    )
    return has_access
