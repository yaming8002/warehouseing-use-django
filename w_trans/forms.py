from decimal import Decimal
from django import forms
from .models import CarInfo


class CarinfoFrom(forms.ModelForm):
    class Meta:
        model = CarInfo
        fields = ["car_number", "firm", "is_count", "value", "remark"]

    car_number = forms.CharField(
        label="車號",
        help_text="(必填)",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    firm = forms.CharField(
        label="公司",
        initial="",
        required=False,  # 设置为非必填
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )

    is_count = forms.BooleanField(
        label="報價",
        initial=False,
        required=False,  # 设置为非必填
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "role": "switch"}
        ),
    )

    remark = forms.CharField(
        label="噸數(備註)",
        required=False,
        initial="",
        widget=forms.Textarea(attrs={"class": "form-control required", "rows": 3}),
    )

    value = forms.DecimalField(
        label="基本台金額",
        required=False,
        initial=Decimal(0),
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )
