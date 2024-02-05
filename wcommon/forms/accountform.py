from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django import forms

from wcommon.models.account import Muser


class AddMuserForm(UserCreationForm):
    class Meta:
        model = Muser
        fields = [
            "username",
            "password1",
            "password2",
            "username_zh",
            "unit",
            "group",
            "email",
        ]

    username = forms.CharField(
        label="帳號", widget=forms.TextInput(attrs={"class": "form-control required"})
    )
    password1 = forms.CharField(
        label="密碼", widget=forms.PasswordInput(attrs={"class": "form-control required"})
    )
    password2 = forms.CharField(
        label="密碼確認", widget=forms.PasswordInput(attrs={"class": "form-control required"})
    )

    email = forms.CharField(
        label="email", 
        required=False,  # 設置為非必填
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    username_zh = forms.CharField(
        label="姓名", widget=forms.TextInput(attrs={"class": "form-control required"})
    )

    unit = forms.CharField(
        label="所屬單位", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    group = forms.ModelChoiceField(
        label="權限",
        queryset=Group.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control required" }),
    )

    widgets = {"password1": forms.PasswordInput(), "password2": forms.PasswordInput()}


# 修改
# class ChangUserForm(UserChangeForm):
#     class Meta:
#         model = Muser
#         fields = ("username_zh", "unit", "group")
