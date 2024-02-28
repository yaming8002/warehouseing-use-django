from django import template

register = template.Library()

menu_category = {
    1: "表單",
    2: "內部倉儲",
    3: "出入報表",
    4: "工地報表",
    5: "資料維護",
    99: "系統管理",
}


@register.simple_tag
def get_category_name(key):
    return menu_category.get(key, "沒有對應的資訊")


constn_state = [(0, "結案"), (1, "運作中"), (2, "尚未動工"), (3, "取消")]


@register.simple_tag
def get_constn_state():
    return constn_state

site_genre = [(0, "內部"), (1, "工地")]

@register.simple_tag
def get_site_genre():
    return site_genre


level = [
    (0, "零星"),
    (1, "第一層"),
    (2, "第二層"),
    (3, "第三層"),
    (4, "第四層"),
    (5, "第五層"),
    (6, "第六層"),
    (7, "第七層")
]


@register.simple_tag
def get_level():
    return level
