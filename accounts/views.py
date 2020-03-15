from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm
from .models import User


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = User(
            email=form.data.get('email'),
            password=make_password(form.data.get('password')),
            type=User.USER
        )
        user.save()
        self.request.session['user'] = user.id
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        if request.session['user']:
            return redirect('home')
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(email=form.data.get('email'))
        self.request.session['user'] = user.id
        return super().form_valid(form)


def logout(request):
    if 'user' in request.session:
        del(request.session['user'])
    return redirect('index')
