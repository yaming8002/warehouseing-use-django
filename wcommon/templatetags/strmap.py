from django import template

register = template.Library()

menu_category = {
    1: "表單",
    2: "內部倉儲",
    3: "出入報表",
    4: "結案項目",
    5: "資料維護",
    99: "系統管理",
}
@register.simple_tag
def get_category_name(key):
    return menu_category.get(key, "沒有對應的資訊")

constn_state = [
    (0, '完工'),
    (1, '運作中'),
    (2, '未動工'),
    (3, '取消')
]

@register.simple_tag
def get_constn_state():
    return constn_state
