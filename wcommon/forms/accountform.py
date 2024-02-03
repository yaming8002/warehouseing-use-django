from django import forms
from django.contrib.auth.forms import UserChangeForm

from wcommon.models import Muser

# 新增
class AddMuserForm(forms.ModelForm):
    class Meta:
        model = Muser
        fields = ["username_zh", "unit", "group", "email"]


# 修改
class ChangUserForm(UserChangeForm):
    class Meta:
        model = Muser
        fields = ("username_zh", "unit", "group")
