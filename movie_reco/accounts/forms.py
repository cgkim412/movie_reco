from django import forms
from django.contrib.auth.hashers import check_password
from .models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(
        error_messages={'required': '이메일을 입력해 주세요.'},
        max_length=128, label='이메일'
    )
    password = forms.CharField(
        error_messages={'required': '비밀번호를 입력해 주세요.'},
        widget=forms.PasswordInput, label='비밀번호'
    )
    confirm_password = forms.CharField(
        error_messages={'required': '비밀번호를 다시 한번 입력해 주세요.'},
        widget=forms.PasswordInput, label='비밀번호 확인'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if len(password) < 4:
                self.add_error('password', '4자 이상의 비밀번호를 사용해 주세요.')

            if password != confirm_password:
                self.add_error('password', '비밀번호가 일치하지 않습니다.')
                self.add_error('confirm_password', '비밀번호가 일치하지 않습니다.')

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            self.add_error('email', '이미 같은 이메일로 가입된 계정이 존재합니다.')


class LoginForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': '이메일을 입력해 주세요.'
        },
        max_length=128, label='이메일'
    )
    password = forms.CharField(
        error_messages={
            'required': '비밀번호를 입력해 주세요.'
        },
        widget=forms.PasswordInput, label='비밀번호'
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.add_error('email', '존재하지 않는 이메일입니다.')
                return

            if not check_password(password, user.password):
                self.add_error('password', '비밀번호가 일치하지 않습니다.')
