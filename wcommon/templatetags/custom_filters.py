from typing import List
from django import template

register = template.Library()

@register.filter
def custom_subtract(value1, value2):
    value1 = float(value1) if isinstance(value1, (float, int, str)) and value1 != '' else 0.0
    value2 = float(value2) if isinstance(value2, (float, int, str)) and value2 != '' else 0.0
    return value1 - value2

@register.filter
def check_done_type(value, encountered_done_type):
    if value != encountered_done_type:
        return True
    return False

@register.filter
def list_index_value(lst:List, index:int):
    return lst[index-1]

@register.filter
def is_not_none(value):
    return value is not None and value != "None"