from decimal import Decimal
from typing import Any, Dict, List
import copy
from django.db.models import F, Sum

from stock.models.material_model import Materials
from trans.models import TransLog, TransLogDetail

steel_list = [
    { "code":"300" ,"unit_name":"米","name" :"H300", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"301" ,"unit_name":"米","name" :"中H300", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"301-1" ,"unit_name":"米","name" :"H300構台樑", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"350" ,"unit_name":"米","name" :"H350", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"351" ,"unit_name":"米","name" :"中H300", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"351-1" ,"unit_name":"米","name" :"H300構台樑", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"400" ,"unit_name":"米","name" :"H400", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"401" ,"unit_name":"米","name" :"中H400", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"401-1" ,"unit_name":"米","name" :"H400構台樑", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"408" ,"unit_name":"米","name" :"H408", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code":"3050" ,"unit_name":"米","name" :"鋼軌", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0}]
component_list= [
    { "code": "10", "unit_name":"片","name": "補強板(接樁用)", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "6300", "unit_name":"片","name": "H300止水板", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "6350", "unit_name":"片","name": "H350止水板", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "6400", "unit_name":"片","name": "H400止水板", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "79", "unit_name":"坪","name": "擋土板5.6.8分", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "44", "unit_name":"坪","name": "黑皮", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "9", "unit_name":"件","name": "防墬網/安全網", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "11", "unit_name":"片","name": "覆工板 1M *2M", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "12", "unit_name":"片","name": "洗車版 2M *2M", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "2105", "unit_name":"片","name": "鋪路鐵板 半", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "21", "unit_name":"片","name": "鋪路鐵板 全", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "13", "unit_name":"顆","name": "千斤頂", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "14", "unit_name":"顆","name": "土壓計", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "16", "unit_name":"座","name": "樓梯", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "19", "unit_name":"片","name": "樓梯鐵板0.8*1.5M", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "20", "unit_name":"片","name": "樓梯鐵板 1*1 / 1*2", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "2201", "unit_name":"支","name": "斜撐 H250.300", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "2202", "unit_name":"支","name": "斜撐 H350", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "4285", "unit_name":"支","name": "H428斜撐", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    { "code": "18", "unit_name":"支","name": "安全步道", "input":{"quantity":0.0,"unit":0.0},"output":{"quantity":0.0,"unit":0.0},"ng_value":0.0},
    ]

# 初始化查询所用的字段字典
values_dict = {
    "code": F("translog__code"),
    "build_date": F("translog__build_date"),
    "transaction_type": F("translog__transaction_type"),
    "name": F("material__name"),
    "level_annotation": F("level"),
}

def build_constn_diff_view(constn) :
    translog = TransLog.objects.filter(constn_site=constn)
    mats = Materials.objects.filter(specification__lt=23)
    transdefaullog = TransLogDetail.objects.filter(
        translog__in=translog, material__in=mats
    )

    steel_table = copy.deepcopy(steel_list)
    for item_d in steel_table:
        mat_code = item_d['code'].split("-")[0]
        construct_case = len(item_d['code'].split("-")) > 1
        if construct_case:
            # 选择remark为"中構台"的项目
            queryset = transdefaullog.filter(
                material__mat_code=mat_code, remark__icontains="構台樑"
            )
        else:
            # 选择remark不为"中構台"的项目
            queryset = transdefaullog.filter(material__mat_code=mat_code).exclude(
                remark__icontains="構台樑"
            )

        total_quantity_and_unit = queryset.values(**values_dict).annotate(
            total_quantity=Sum("quantity"),
            total_unit=Sum("all_unit"),
        )

        for item in total_quantity_and_unit:
            update_items(item_d,item,item["transaction_type"] == "IN",True)
        
    components = copy.deepcopy(component_list) 
    for item_d in components:
        mat_code = item_d['code']

        total_quantity_and_unit = queryset.values(**values_dict).annotate(
            total_quantity=Sum("quantity"),
        )

        for item in total_quantity_and_unit:
            update_items(item_d,item,item["transaction_type"] == "IN",False)

    
    return steel_table,components
    
def update_items(dct,item, transaction_type ,has_unit ):
    if transaction_type:
        dct['input']["quantity"] += float(item["total_quantity"])
        dct['input']["unit"] += float(item["total_unit"]) if has_unit  else  float(0)
    else:
        dct['output']["quantity"] += float(item["total_quantity"])
        dct['output']["unit"] += float(item["total_unit"]) if has_unit  else  float(0)

