import random
import string

def random_string_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))