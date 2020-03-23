import random
import string
from django.utils.crypto import get_random_string


def generate_random_email(length):
    return get_random_string(length) + "@random.user"

def generate_random_password(length):
    return get_random_string(length)