import random
import string


def env_to_bool(value):
    """Convert env variables from .env file to boolean"""
    if not isinstance(value, bool):
        return value.upper() == "TRUE"
    return value


def random_string_generator(size=6, chars=string.digits):
    """Generate a random string of digits for slugs"""
    return "".join(random.choice(chars) for _ in range(size))
