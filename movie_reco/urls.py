"""movie_reco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import index, about, home
from accounts.views import LoginView, RegisterView, logout, guest_login
from ratings.views import evaluate, my_ratings, RatingAPI
from movies.views import MovieAPI, SimpleMovieAPI
from recommender.views import RecoListAPI

api_base_urls = [
    path('evaluate/', evaluate, name='evaluate'),
    path('movie/', home, name='movie'),
    path('recommendation/', home, name='recommendation')
]

api_urls = [
    path('evaluate/<int:movie_id>/', RatingAPI.as_view()),
    path('movie/<int:movie_id>/', MovieAPI.as_view()),
    path('movie/<int:movie_id>/lite/', SimpleMovieAPI.as_view()),
    path('recommendation/<int:limit>/', RecoListAPI.as_view()),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('about/', about, name='about'),
    path('login/', LoginView.as_view(), name='login'),
    path('guest/', guest_login, name='guest'),
    path('logout/', logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('evaluate/record/', my_ratings, name='eval_record'),
] + api_base_urls + api_urls