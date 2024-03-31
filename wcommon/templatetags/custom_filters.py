from django import template

register = template.Library()

@register.filter
def custom_subtract(value1, value2):
    return value1 - value2

@register.filter
def check_done_type(value, encountered_done_type):
    if value != encountered_done_type:
        return True
    return False

