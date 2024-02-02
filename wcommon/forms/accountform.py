from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from wcommon.models import Muser


# 查詢
class MuserSearchFrom(UserCreationForm):
    search_username_zh = forms.CharField(label="姓名", max_length=30)
    search_unit = forms.CharField(label="所屬單位", max_length=30)
    search_group = forms.CharField(label="權限群組", max_length=30)

    class Meta:
        model = Muser
        fields = "__all__"


# 新增
class AddUserForm(UserCreationForm):
    class Meta:
        model = Muser
        fields = "__all__"


# 修改
class ChangUserForm(UserChangeForm):
    class Meta:
        model = Muser
        fields = ("username_zh", "unit", "group")
