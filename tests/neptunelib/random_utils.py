import random
import string
import uuid


def a_string():
    char_set = string.ascii_letters
    return ''.join(random.sample(char_set * 10, 10))


def a_uuid_string():
    return str(uuid.uuid4())
