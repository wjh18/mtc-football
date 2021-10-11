import random
import string


def random_string_generator(size=6, chars=string.digits):
    """Generate a random string of digits for slugs"""
    return ''.join(random.choice(chars) for _ in range(size))
