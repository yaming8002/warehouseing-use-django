from django import forms
from django.utils import timezone
from stock.models.site_model import SiteInfo


from wcom.templatetags import constn_state


class SiteInfoForm(forms.ModelForm):
    class Meta:
        model = SiteInfo
        fields = [
            "code",
            "owner",
            "name",
            "address",
            "crate_date",
            "member",
            "counter",
            "company",
            "is_steel_done",
            "is_rail_done",
            "state",
            "done_date",
            "remark",
        ]
        labels = {
            "code": "工地代號",
            "owner": "業主",
            "name": "工程名稱",
            "address": "地點",
            "crate_date": "發案日期",
            "member": "現場人員",
            "counter": "會計人員",
            "company": "公司行號",
            "is_steel_done":"鋼樁結案",
            "is_rail_done":"鋼軌結案",   
            "state": "狀態",
            "done_date": "結案日期",
            "remark": "備註",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 如果是新增操作，则设置 crate_date 字段的初始值为当前日期
        if not self.instance:
            self.initial["crate_date"] = timezone.now().date()
            self.fields["done_date"].widget = forms.HiddenInput()
            self.fields["is_steel_done"].widget = forms.HiddenInput()
            self.fields["is_rail_done"].widget = forms.HiddenInput()
            self.fields["code"].widget.attrs["readonly"] = True
        else:
            self.fields["code"].widget.attrs["readonly"] = False
            if not self.instance.is_steel_done:
                self.fields["is_steel_done"].widget = forms.HiddenInput()
            if not self.instance.is_rail_done:
                self.fields["is_rail_done"].widget = forms.HiddenInput()

    code = forms.CharField(
        label="工地代號",
        help_text="*",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    owner = forms.CharField(
        label="業主",
        help_text="*",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    name = forms.CharField(
        label="工程名稱",
        help_text="*",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    address = forms.CharField(
        label="地點",
        required=False,  # 允许字段为空
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    crate_date = forms.DateField(
        label="發案日期",
        initial=timezone.now().date(),
        widget=forms.HiddenInput(),
    )

    member = forms.CharField(
        label="現場人員",
        required=False,  # 允许字段为空
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    counter = forms.CharField(
        label="會計人員",
        required=False,  # 允许字段为空
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    company = forms.CharField(
        label="公司行號",
        required=False,  # 允许字段为空
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    is_steel_done = forms.BooleanField(
        label="鋼樁結案", required=False,widget=forms.CheckboxInput()
    )

    is_rail_done = forms.BooleanField(
        label="鋼軌結案", required=False, widget=forms.CheckboxInput()
    )

    state = forms.IntegerField(
        label="狀態", initial=2, widget=forms.Select(choices=constn_state)
    )

    done_date = forms.DateField(
        label="結案日期",
        initial=None,
        required=False,  # 允许字段为空
        widget=forms.HiddenInput(),
    )

    remark = forms.CharField(
        label="備註",
        required=False,  # 允许字段为空
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
