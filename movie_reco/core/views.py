from django.shortcuts import render, redirect
from accounts.utils import get_user_obj
from accounts.decorators import login_required


def index(request):
    user = get_user_obj(request)
    if user is None:
        return render(request, 'index.html')
    else:
        return redirect('home')


@login_required
def home(request):
    user = get_user_obj(request)
    if user.ratings.all().count() < 10:
        return redirect('evaluate')
    return render(request, 'home.html', {'user': user.email})


@login_required
def about(request):
    return render(request, 'about.html')


@login_required
def author(request):
    return render(request, 'author.html')