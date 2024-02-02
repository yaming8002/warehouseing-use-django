from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from ..wcommon.models import Muser


# 新增
class CrateUserForm(UserCreationForm):
    class Meta:
        model = Muser
        fields = "__all__"


# 修改
class ChangUserForm(UserChangeForm):
    class Meta:
        model = Muser
        fields = ("username_zh", "unit", "group")
