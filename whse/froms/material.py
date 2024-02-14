from django.db import models

from django import forms
from whse.models.material import MatCat, MatList, MatSpec


class MatListForm(forms.ModelForm):
    class Meta:
        model = MatList
        fields = [
            "mat_code",
            "name",
            "category",
            "specification",
            "is_consumable",
            "is_divisible",
            "unit_of_division",
        ]
        labels = {
            "mat_code": "物料編號",
            "name": "料名",
            "category": "分類",
            "specification": "規格",
            "is_consumable": "是否為耗材",
            "is_divisible": "是否可拆分",
            "unit_of_division": "拆分單位",
        }

    mat_code = forms.CharField(
        label="物料編號",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )
    
    name = forms.CharField(
        label="料名",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )
    
    category = forms.ModelChoiceField(
        label="分類",
        queryset=MatCat.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control required"}),
    )

    specification = forms.ModelChoiceField(
        label="規格",
        queryset=MatSpec.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-control required"}),
    )

    is_consumable = forms.BooleanField(
        label="是否為耗材",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_divisible = forms.BooleanField(
        label="是否可拆分",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    unit_of_division = forms.CharField(
        label="拆分單位",
        widget=forms.TextInput(attrs={"class": "form-control required"}),
    )