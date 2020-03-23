from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm
from .models import User
from .utils import generate_random_email, generate_random_password


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_email'] = generate_random_email(16)
        return context


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        try:
            request.session['user']
        except KeyError:
            return super().get(request, *args, **kwargs)
        else:
            return redirect('home')

    def form_valid(self, form):
        user = User.objects.get(email=form.data.get('email'))
        self.request.session['user'] = user.id
        return super().form_valid(form)


def logout(request):
    if 'user' in request.session:
        del(request.session['user'])
    return redirect('index')


def guest_login(request):
    if 'user' in request.session:
        del(request.session['user'])
    new_user = User(email=generate_random_email(16),
                    password=generate_random_password(16),
                    type=User.USER
    )
    new_user.save()
    request.session['user'] = new_user.id
    return redirect('home')
