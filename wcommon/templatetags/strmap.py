from django import template

register = template.Library()


@register.simple_tag
def get_category_name(key):
    return menu_category.get(key, "沒有對應的資訊")


menu_category = {
    1: "表單",
    2: "內部倉儲",
    3: "出入報表",
    4: "結案項目",
    5: "資料維護",
    99: "系統管理",
}
