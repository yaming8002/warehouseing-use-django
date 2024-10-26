from decimal import Decimal
from django import forms
from .models import CarInfo


class CarinfoFrom(forms.ModelForm):
    class Meta:
        model = CarInfo
        fields = ["car_number", "firm", "is_count", "value", "remark"]

    car_number = forms.CharField(
        label="車號",
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

# class TransLogDetailForm(forms.ModelForm):
#     LEVEL_CHOICES = [
#         (999, "---"),
#         (0, "零星"),
#         (1, "第一層"),
#         (2, "第二層"),
#         (3, "第三層"),
#         (4, "第四層"),
#         (5, "第五層"),
#         (6, "第六層"),
#         (7, "第七層"),
#     ]

#     detial_id =forms.CharField(
#         label="id",
#         widget=forms.HiddenInput(),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )
#     # Define form fields manually that are not directly part of the model
#     translog_code = forms.CharField(
#         label="單號",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )

#     site_code = forms.CharField(
#         label="工地編號",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )
#     owner = forms.CharField(
#         label="業主",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )
#     site_name = forms.CharField(
#         label="名稱",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )
#     material_code = forms.CharField(
#         label="物料代號",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )

#     material_name = forms.CharField(
#         label="物料名稱",
#         widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
#         disabled=True,  # 設為不可編輯
#         required=False,
#     )

#     level = forms.ChoiceField(
#         label="施工層別",
#         choices=LEVEL_CHOICES,
#         widget=forms.Select(attrs={"class": "form-control"}),
#     )
#     unit = forms.DecimalField(
#         label="單位量",
#         widget=forms.NumberInput(attrs={"class": "form-control"})
#     )
#     quantity = forms.DecimalField(
#         label="數量",
#         widget=forms.NumberInput(attrs={"class": "form-control"})
#     )

#     remark = forms.CharField(
#         label="備註",
#         widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
#     )

#     class Meta:
#         model = TransLogDetail
#         fields = ['translog_code', 'site_code']  # Only direct fields from the model

#     def __init__(self, *args, **kwargs):
#         super(TransLogDetailForm, self).__init__(*args, **kwargs)
#         instance = kwargs.get('instance')
#         if instance:
#             self.initial['detial_id'] = instance.id
#             self.initial['translog_code'] = instance.translog.code if instance.translog else ''
#             self.initial['site_code'] = instance.translog.constn_site.code if instance.translog and instance.translog.constn_site else ''
#             self.initial['owner'] = instance.translog.constn_site.owner if instance.translog and instance.translog.constn_site else ''
#             self.initial['site_name'] = instance.translog.constn_site.name if instance.translog and instance.translog.constn_site else ''
#             self.initial['material_code'] = instance.material.mat_code if instance.material else ''
#             self.initial['material_name'] = instance.material.name if instance.material else ''
#             self.initial['unit'] = instance.unit
#             self.initial['quantity'] = instance.quantity
#             self.initial['remark'] = instance.remark  if instance.remark and instance.remark != "None" else ""
#             if instance.material and not instance.material.is_divisible:
#                 self.fields['unit'].widget = forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"})

#     def save(self, commit=True):
#         """
#         Save this form's self.instance object if commit=True. Otherwise, add
#         a save_m2m() method to the form which can be called after the instance
#         is saved manually at a later time. Return the model instance.
#         """
#         if self.errors:
#             raise ValueError(
#                 "The %s could not be %s because the data didn't validate."
#                 % (
#                     self.instance._meta.object_name,
#                     "changed",
#                 )
#             )

#             # If committing, save the instance and the m2m data immediately.
#         original= TransLogDetail.objects.get(id = self.detial_id)
#         unit =  self.instance.unit
#         quantity = self.instance.quantity
#         all_unit = unit * quantity
#         mat = Materials.get_item_by_code(self.instance.material.mat_code, self.instance.remark, unit)
#         diff_quantity = self.instance.quantity - original.quantity
#         diff_all_unit = all_unit - original.all_unit

#         if mat.id == original.material.id:
#             if  diff_quantity == 0 and diff_all_unit == 0:
#                 self.instance.save()
#                 return 
#             tran = self.instance.translog
#             is_stock_add = tran.transaction_type == "IN"
#             MainStock.move_material(mat, quantity, all_unit, is_stock_add)

#             if DoneSteelReport.add_new_mat( tran.constn_site, tran.turn_site, tran.build_date, is_stock_add, mat, quantity, all_unit ,remark ):
#                 """if this case not new material"""
#                 ConStock.move_material( tran.constn_site, mat, quantity, all_unit, not is_stock_add )
#                 SteelReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity, all_unit )
                
#             RailReport.add_report( tran.constn_site, tran.build_date, is_stock_add, mat, quantity )
#             BoardReport.add_report(tran.constn_site, self.instance.remark, is_stock_add, mat, quantity)
#         elif 

#         self.instance.save()
        


#         return self.instance
  