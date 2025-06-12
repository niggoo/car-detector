import hashlib
import random
import string

from pydantic import BaseModel


def generate_random_hash() -> str:
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    hash_object = hashlib.sha256(random_string.encode())
    return hash_object.hexdigest()


class User(BaseModel):
    username: str
    password: str