from accounts.models import User


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

