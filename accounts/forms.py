from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class SignupForm(UserCreationForm):
    username = forms.CharField(label="아이디")
    email = forms.EmailField(label="이메일", required=True)
    phone = forms.CharField(label="전화번호", required=True)
    address = forms.CharField(label="주소", required=True)
    company = forms.CharField(label="소속(선택)", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "아이디"
        self.fields["username"].required = True
        self.fields["email"].label = "이메일 주소"
        self.fields["email"].required = True


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ["phone","company","address"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.fields["phone"].label = "전화번호"
        self.fields["phone"].required = True

        self.fields["address"].label = "주소"
        self.fields["address"].required = True

        self.fields["company"].label = "소속"
        self.fields["company"].required = False