from django.shortcuts import render

from stock.service.steel_brace import build_steel_brace_table
from stock.service.steel_diff_summary import build_constn_diff_view
from stock.service.steel_pile import build_steel_ng_table, build_steel_pile_table
from stock.service.steel_component import build_component_table
from stock.models.site_model import SiteInfo
from stock.service.steel_tools import build_tools_table
from stock.utils import get_global_component_list, get_global_tool_list
from wcom.templatetags.strmap import get_level

# Create your views here.


def steel_brace_view(request):
    # 鋼樁
    context = {}
    table_level = 7
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")
        constn = SiteInfo.objects.filter(genre=1)
        show = False
        if owner:
            constn = constn.filter(owner=owner)
            show = True
        if code:
            constn = constn.filter(code=code)
            show = True
        if name:
            constn = constn.filter(name=name)
            show = True

        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level

        if show and constn.exists():
            context["steel_pile_table"] = build_steel_brace_table(
                constn.get(), table_level
            )
            context["constn"] = constn.get()
            context["select_level"] = [x for x in get_level() if (x[0] > 0)]

    context["table_level"] = table_level
    context["column_count"] = range((table_level + 1) * 2)
    return render(request, "constn_report/steel_brace.html", context)


def steel_pile_view(request):
    # 将查询结果传递给模板
    context = {}
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")
        constn = SiteInfo.objects.filter(genre=1)
        show = False
        if owner:
            constn = constn.filter(owner=owner)
            show = True
        if code:
            constn = constn.filter(code=code)
            show = True
        if name:
            constn = constn.filter(name=name)
            show = True

        if show and constn.exists():
            context["steel_pile_table"] = build_steel_pile_table(constn.get())
            context["steel_ng_table"] = build_steel_ng_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(2)

    return render(request, "constn_report/steel_pile.html", context)


def component_view(request):
    # 将查询结果传递给模板
    context = {}
    table_level = 7
    component_list = get_global_component_list()
    selected_items = []
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")
        selected_items = request.POST.getlist("selected_items")

        constn_obj = SiteInfo.get_obj_by_value(
            genre=1, owner=owner, code=code, name=name
        )
        # print(constn_obj.query)
        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level
        selected_items_map = [
            item for item in component_list if str(item["id"]) in selected_items
        ]

        if constn_obj.exists():
            context["constn"] = constn_obj.get()
            context["steel_pile_table"] = build_component_table(
                context["constn"], table_level, selected_items_map
            )

            context["select_level"] = [x for x in get_level() if (x[0] > 0)]

    context["com_cla"] = [{"id": 1, "name": "主要"}, {"id": 2, "name": "其他"}]
    context["component_list"] = component_list
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range((table_level + 1) * 2)
    return render(request, "constn_report/component.html", context)


def tool_view(request):
    # 将查询结果传递给模板
    context = {}
    table_level = 7
    tool_list = get_global_tool_list()
    selected_items = []
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")
        selected_items = request.POST.getlist("selected_items")

        constn_obj = SiteInfo.get_obj_by_value(
            genre=1, owner=owner, code=code, name=name
        )

        # print(constn_obj.query)
        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level
        # 使用字典推導式來過濾 tool_list 中的項目，並建立 id 到 name 的映射
        selected_items_map = [
            item for item in tool_list if str(item["id"]) in selected_items
        ]

        if constn_obj.exists():
            context["constn"] = constn_obj.get()
            context["steel_pile_table"] = build_tools_table(
                context["constn"], table_level, selected_items_map
            )

            context["select_level"] = [x for x in get_level() if (x[0] > 0)]


    context["tool_list"] = tool_list
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range((table_level + 1) * 2)
    return render(request, "constn_report/steel_tools.html", context)


def constn_diff_view(request):
    # 将查询结果传递给模板
    context = {}
    table_level = 7
    selected_items = []
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")

        constn_obj = SiteInfo.get_obj_by_value(
            genre=1, owner=owner, code=code, name=name
        )
        context["constn"] = constn_obj.get()
        if constn_obj.exists():
            context["steel_table"], context["components"] = build_constn_diff_view(
                context["constn"]
            )

    # context["mat_tree"] = mat_tree
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/steel_diff.html", context)
