from django.shortcuts import redirect
from .models import User


def login_required(function):
    def wrap(request, *args, **kwargs):
        user = request.session.get('user')
        if user is None or not user:
            return redirect('index')
        try:
            User.objects.get(id=user)
        except User.DoesNotExist:
            return redirect('index')
        else:
            return function(request, *args, **kwargs)
    return wrap


def admin_required(function):
    def wrap(request, *args, **kwargs):
        user = request.session.get('user')

        if user is None or not user:
            return redirect('index')

        if User.objects.get(id=user).type != User.ADMIN:
            return redirect('home')
        return function(request, *args, **kwargs)

    return wrap
