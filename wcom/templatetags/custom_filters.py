from decimal import Decimal
from typing import List
from django import template
from django.db import models
register = template.Library()

@register.filter
def dict_get_value(dct, key):
    # 检查键是否存在于字典中
    if key in dct:
        val = dct[key]
        # 检查值是否为 None 或 'None'
        if val is None or val == 'None':
            return ''
        # 检查值是否为 int 或 Decimal，并且值是否为 0
        if isinstance(val, (int, Decimal)) and val == 0:
            return ''
        return val
    return ''

@register.filter
def steel_model_get_value(dct, key):
    key = f'm_{key}'
    if key in dct:
        val = dct[key]
        # 检查值是否为 None 或 'None'
        if val is None or val == 'None':
            return ''
        # 检查值是否为 int 或 Decimal，并且值是否为 0
        if isinstance(val, (int, Decimal)) and val == 0:
            return 0
        return val
    return 0

@register.filter
def subtract(value1, value2):
    value1 = (
        float(value1)
        if isinstance(value1, (Decimal, float, int, str)) and value1 != ""
        else 0.0
    )
    value2 = (
        float(value2)
        if isinstance(value2, (Decimal, float, int, str)) and value2 != ""
        else 0.0
    )
    return value1 - value2


@register.filter
def check_done_type(value, encountered_done_type):
    if value != encountered_done_type:
        return True
    return False


@register.filter
def list_index_value(lst: List, index: int):
    return lst[index - 1]


@register.filter
def is_not_none(value):
    return value is not None and value != "None"


@register.filter
def kg_to_meter(mat_code,kg_value):
    dct = {
        "3050": 50,
        "300": 93,
        "301": 93,
        "350": 135,
        "351": 135,
        "400": 172,
        "401": 172,
        "408": 197,
        "414": 232,
        "4141": 232,
    }

    return f"{kg_value/dct.get(mat_code,1):.2f}"

@register.filter
def month_full(month):
    if month > 9:
        return f"{month}"

    return f"0{month}"
