from django.http import JsonResponse
from django.shortcuts import render

from stock.models.steel_pile_model import SteelPile
from stock.service.steel_brace import build_steel_brace_table
from stock.service.steel_diff_summary import build_constn_diff_view
from stock.service.steel_pile import build_steel_ng_table, build_steel_pile_table
from stock.service.steel_component import build_component_table
from stock.models.site_model import SiteInfo
from stock.service.steel_tools import build_tools_table
from stock.utils import get_global_component_list, get_global_tool_list
from trans.models.trans_model import TransLogDetail
from wcom.templatetags.strmap import get_level
from wcom.utils.uitls import value_to_decimal

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


def steel_pile_edit_view(request):
    # 鋼樁
    context = {}
    if request.method == "GET":
        id = request.GET.get("id")
        context["item"] = SteelPile.objects.get(id=id)
        context["title"] = "編輯構台樑"
        return render(request, "constn_report/steel_pile_edit.html", context)
    else:
        id = request.POST.get("id")
        item = SteelPile.objects.get(id=id)
        truss_quantity = value_to_decimal(request.POST.get("truss_quantity"))
        truss_unit = value_to_decimal(request.POST.get("truss_unit"))
        quantity = value_to_decimal(request.POST.get("quantity"))
        unit = value_to_decimal(request.POST.get("unit"))
        if truss_quantity == 0 and truss_unit == 0 and quantity == 0 and unit == 0:
            item.delete()
        if truss_quantity == 0 and truss_unit == 0:
            item.is_mid = False
            item.remark = item.remark.replace("None", "").replace("構台樑", "").replace("修改", "") + "修改"
            item.save()
        elif quantity == 0 and unit == 0:
            item.remark = item.remark.replace("None", "").replace("修改", "")+ "修改"
            item.is_mid = True
            item.save()
        else:
            item.is_mid = False
            item.quantity = quantity
            item.unit = unit
            item.remark = item.remark.replace("None", "").replace("構台樑", "").replace("修改", "")  + " 修改"
            item.save()
            SteelPile.objects.create(
                translog=item.translog,
                material=item.material,
                is_mid=True,
                is_ng=item.is_ng,
                quantity=truss_quantity,
                unit=truss_unit,
                remark="構台樑" + "  修改",
            )

        context = {"msg": "成功"}
        return JsonResponse(context)


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
