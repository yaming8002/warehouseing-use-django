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

site_genre = [(0, "內部倉"), (1, "工地"),(2,"租料倉"),(3,"加工廠"),(4,"維修廠"),(5,"供應商")]

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
def get_level_all():
    return level

@register.simple_tag
def get_level():
    return level[1:]


done_type_map = [
    (0, "無"),
    (1, "賣斷"),
    (2, "總數變動"),
    (3, "異動變動"),
    (4, "切除變動")
]

@register.simple_tag
def get_done_type():
    return done_type_map


@register.simple_tag
def get_done_type_value(key):
    for num,name in done_type_map:
        if key==num:
            return name
    return "沒有對應的資訊"


@register.simple_tag
def define(val=None):
  return val