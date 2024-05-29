from decimal import Decimal
from typing import List
from django import template

register = template.Library()


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
