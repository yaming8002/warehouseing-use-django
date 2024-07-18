from django import forms

from stock.models.stock_model import Stock


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['id', 'siteinfo', 'material', 'quantity', 'total_unit']
        labels = {
            "mat_code": "物料編號",
            "mat_code2": "入料編號",
            "mat_code3": "出料編號",
            "name": "料名",
            "category": "分類",
            "specification": "規格",
            "is_consumable": "是否為耗材",
            "is_divisible": "是否可拆分",
            "unit_of_division": "拆分單位",
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'total_unit': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super(StockForm, self).__init__(*args, **kwargs)

        # 設置siteinfo和material相關欄位為只讀
        self.fields['siteinfo'].widget = forms.TextInput(attrs={
            'readonly': True, 'value': self.instance.siteinfo.name if self.instance.siteinfo else ''
        })
        self.fields['material'].widget = forms.TextInput(attrs={
            'readonly': True, 'value': self.instance.material.mat_code if self.instance.material else ''
        })
        # 若需要更多的material屬性，可以類似上面的方式加入
        self.fields['material'].widget.attrs.update({
            'name': 'readonly', 'value': self.instance.material.name if self.instance.material else ''
        })
        self.fields['material'].widget.attrs.update({
            'category': 'readonly', 'value': self.instance.material.category if self.instance.material else ''
        })
        self.fields['material'].widget.attrs.update({
            'specification': 'readonly', 'value': self.instance.material.specification if self.instance.material else ''
        })

        # 確保只有quantity和total_unit可被編輯
        for field_name in self.fields:
            if field_name not in ['quantity', 'total_unit']:
                self.fields[field_name].disabled = True
