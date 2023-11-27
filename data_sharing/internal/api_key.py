from secrets import token_urlsafe

from data_sharing.constants import constants
from data_sharing.internal.hashing import get_key_hash


def generate_api_key():
    key = token_urlsafe(constants.API_KEY_BYTES_LENGTH)
    hashed_key = get_key_hash(key)
    return key, hashed_key
