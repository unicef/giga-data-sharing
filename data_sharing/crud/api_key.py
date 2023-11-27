from secrets import token_urlsafe

from data_sharing.constants import constants


def generate_api_key():
    return token_urlsafe(constants.API_KEY_BYTES_LENGTH)
