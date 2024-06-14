from xml.dom import ValidationErr
from django import forms
from django.contrib.auth.forms import PasswordChangeForm , UserCreationForm
from django.utils.translation import gettext_lazy as _

from wcom.models.account import Muser
from wcom.models.user_group import UserGroup


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
        label="密碼",
        widget=forms.PasswordInput(attrs={"class": "form-control required"}),
    )
    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={"class": "form-control required"}),
    )

    email = forms.CharField(  # 暫時先關閉
        label="",
        required=False,  # 設置為非必填
        widget=forms.TextInput(
            attrs={"class": "form-control hide", "style": "display: none;"}
        ),
    )

    username_zh = forms.CharField(
        label="姓名", widget=forms.TextInput(attrs={"class": "form-control required"})
    )

    unit = forms.CharField(
        label="所屬單位", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    group = forms.ModelChoiceField(
        label="權限",
        queryset=UserGroup.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control required"}),
    )


class CustomPasswordChangeForm(PasswordChangeForm):
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self.fields["old_password"].label = _("舊密碼")
         self.fields["new_password1"].label = _("新密碼")
         self.fields["new_password1"].help_text=""
         self.fields["new_password2"].label = _("請再輸入您的新密碼")

     class Meta:
         model = Muser
    
     def clean_new_password1(self):
         new_password1 = self.cleaned_data.get('new_password1')
         if len(new_password1) < 8:
             raise ValidationErr(_('新密碼長度必須大於8個字。'))
         return new_password1

     def clean_new_password2(self):
         new_password1 = self.cleaned_data.get('new_password1')
         new_password2 = self.cleaned_data.get('new_password2')
         if new_password1 and new_password2:
             if new_password1 != new_password2:
                 raise ValidationErr(_('兩次輸入的新密碼不一致。'))
         return new_password2
