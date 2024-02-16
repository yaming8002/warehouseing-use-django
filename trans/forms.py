

# from django import forms
# from constn.models import Construction

# from trans.models import TransportLog
# from whse.models.whse import WhseList

# from django import forms
# from .models import TransportDetailLog, TransportLog, Construction, WhseList

# class TransportLogFrom(forms.ModelForm):
#     class Meta:
#         model = TransportDetailLog
#         ....
    
#     TransportDetailLog.logistics.code = forms.CharField(
#         label="單號", widget=forms.TextInput(attrs={"class": "form-control required"})
#     )





# class AddMuserForm(UserCreationForm):
#     class Meta:
#         model = Muser
#         fields = [
#             "username",
#             "password1",
#             "password2",
#             "username_zh",
#             "unit",
#             "group",
#             "email",
#         ]

#     username = forms.CharField(
#         label="帳號", widget=forms.TextInput(attrs={"class": "form-control required"})
#     )
#     password1 = forms.CharField(
#         label="密碼",
#         widget=forms.PasswordInput(attrs={"class": "form-control required"}),
#     )
#     password2 = forms.CharField(
#         label="密碼確認",
#         widget=forms.PasswordInput(attrs={"class": "form-control required"}),
#     )

#     email = forms.CharField(  # 暫時先關閉
#         label="",
#         required=False,  # 設置為非必填
#         widget=forms.TextInput(
#             attrs={"class": "form-control hide", "style": "display: none;"}
#         ),
#     )

#     username_zh = forms.CharField(
#         label="姓名", widget=forms.TextInput(attrs={"class": "form-control required"})
#     )

#     unit = forms.CharField(
#         label="所屬單位", widget=forms.TextInput(attrs={"class": "form-control"})
#     )

#     group = forms.ModelChoiceField(
#         label="權限",
#         queryset=UserGroup.objects.filter(is_active=True),
#         empty_label=None,
#         widget=forms.Select(attrs={"class": "form-control required"}),
#     )