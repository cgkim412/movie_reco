from accounts.models import User
from django.utils.crypto import get_random_string


def get_user_obj(request):
    user_id = request.session.get('user')
    if user_id is None:
        return None
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    else:
        return user


def generate_random_email(length):
    return get_random_string(length) + "@random.user"


def generate_random_password(length):
    return get_random_string(length)