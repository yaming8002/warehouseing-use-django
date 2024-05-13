from django.shortcuts import render

from stock.util.steel_brace import build_steel_brace_table
from stock.util.steel_diff_summary import build_constn_diff_view
from stock.util.steel_pile import build_steel_ng_table, build_steel_pile_table
from stock.util.steel_component import component_map, build_component_table, mat_tree
from stock.models.site_model import SiteInfo
from wcom.templatetags.strmap import get_level

# Create your views here.


def steel_brace_view(request):
    # 鋼樁 
    context = {}
    table_level = 7
    if request.method == "GET":
        owner = request.GET.get("owner")
        code = request.GET.get("code")
        name = request.GET.get("name")
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

        get_level_val = request.GET.get("level")
        table_level = int(get_level_val) if get_level_val else table_level

        if show and constn.exists():
            context["steel_pile_table"] = build_steel_brace_table(
                constn.get(), table_level
            )
            context["constn"] = constn.get()
            context["select_level"] = [x for x in get_level() if (x[0] > 0)]

    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/steel_brace.html", context)


def steel_pile_view(request):
    # 将查询结果传递给模板
    context = {}
    if request.method == "GET":
        owner = request.GET.get("owner")
        code = request.GET.get("code")
        name = request.GET.get("name")
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
    selected_items = []
    if request.method == "POST":
        owner = request.POST.get("owner")
        code = request.POST.get("code")
        name = request.POST.get("name")
        selected_items = request.POST.getlist("selected_items")

        constn_obj = SiteInfo.get_obj_by_value(
            genre=1, owner=owner, code=code, name=name
        )
        print(constn_obj.query)
        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level

        selected_items_map = {key: component_map[key] for key in selected_items}

        if constn_obj.exists():
            context["constn"] = constn_obj.get()
            context["steel_pile_table"] = build_component_table(
                context["constn"], table_level, selected_items_map
            )

            context["select_level"] = [x for x in get_level() if (x[0] > 0)]

    context["mat_tree"] = mat_tree
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/component.html", context)


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
            context["steel_table"],context["components"] = build_constn_diff_view(context["constn"])

    context["mat_tree"] = mat_tree
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/steel_diff.html", context)
