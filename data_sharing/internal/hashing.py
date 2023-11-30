from passlib.context import CryptContext

from data_sharing.constants import constants

hash_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__rounds=constants.ARGON2_NUM_ITERATIONS,
)


def verify_key(plain_key: str, hashed_key: str):
    return hash_context.verify(plain_key, hashed_key)


def get_key_hash(key: str):
    return hash_context.hash(key)
