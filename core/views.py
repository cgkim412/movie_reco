from django.shortcuts import render, redirect
from accounts.decorators import login_required
from accounts.models import User
from rest_framework.renderers import JSONRenderer
from recommender.reco_interface import RECO_INTERFACE

# Create your views here.

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

def index(request):
    user = get_user_obj(request)
    if user is None:
        return render(request, 'index.html')
    else:
        return redirect('home')

@login_required
def home(request):
    user = get_user_obj(request)

    # redirect to evaluation page if user has less than 10 ratings
    if user.ratings.all().count() < 10:
        return redirect('evaluate')

    reco_list = RECO_INTERFACE.get_recommendation(user, limit=100)

    res_data = []
    for label, items in reco_list.items():
        entry = {"label": label, "items": items}
        res_data.append(entry)
    json = JSONRenderer().render(res_data)

    return render(request, 'home.html', {'user': user.email, 'reco_list': json.decode('utf8')})

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def author(request):
    return render(request, 'author.html')
