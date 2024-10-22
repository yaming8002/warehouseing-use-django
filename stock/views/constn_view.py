import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from stock.models.steel_pile_model import SteelPile
from stock.service.steel_brace import build_steel_brace_table
from stock.service.steel_diff_summary import build_constn_diff_view
from stock.service.steel_pile import build_steel_ng_table, build_steel_pile_table
from stock.service.steel_component import build_component_table
from stock.models.site_model import SiteInfo
from stock.service.steel_tools import build_tools_table
from stock.utils import (
    fill_diff_table_excel,
    filter_selected_items,
    get_global_component_list,
    get_global_site_json,
    get_global_tool_list,
    get_table_level,
)
from warehousing_server import settings
from wcom.utils.uitls import value_to_decimal
from django.template.loader import render_to_string



def steel_control_view(request):
    """主控視圖，根據 POST 請求的 table_name 執行不同邏輯"""

    context = {
        "sitelist": get_global_site_json(),
        "tables": [
            {"code": "pile", "name": "鋼樁"},
            {"code": "braces", "name": "支撐"},
            {"code": "component", "name": "配件"},
            {"code": "tool", "name": "工具"},
        ],
        "com_cla": [{"id": 1, "name": "主要"}, {"id": 2, "name": "其他"}],
        "component_list": get_global_component_list(),
        "tool_list": get_global_tool_list(),
        "table_level": 7,
    }

    if request.method == "POST":
        site_code = request.POST.get("site_code")
        table_name = request.POST.get("table_name")
        selected_items = request.POST.getlist("selected_items", [])
        table_level = get_table_level(request.POST.get("level"))

        constn = SiteInfo.get_site_by_code(site_code)
        if not constn:
            return JsonResponse({"success": False, "message": "無效的站點代碼"})

        context.update(
            {
                "constn": constn,
                "table_level": table_level,
                "column_count": range((table_level + 1) * 2),
            }
        )

        # 根據 table_name 渲染對應模板為字符串
        html_str = render_table_to_string(
            context, table_name, selected_items, table_level ,request
        )

        for x in context["tables"]:
            if x["code"] == table_name:
                context["table_name"] = x["name"]
        # 返回包含渲染後的 HTML 字符串
        # return JsonResponse({"success": True, "html": html_str})
        context["value"] = html_str
    return render(request, "constn_report/report_control.html", context)


def render_table_to_string(context, table_name, selected_items, table_level,request):
    """根據 table_name 渲染對應模板，並返回 HTML 字符串"""
    context["u_permission"] = request.session.get("u_permission")

    if table_name == "braces":
        context["steel_pile_table"] = build_steel_brace_table(
            context["constn"], table_level
        )
        return render_to_string("constn_report/brace_table.html", context)

    elif table_name == "pile":
        context["steel_pile_table"] = build_steel_pile_table(context["constn"])
        context["steel_ng_table"] = build_steel_ng_table(context["constn"])
        return render_to_string("constn_report/pile_table.html", context)

    elif table_name == "component":
        selected_items_map = filter_selected_items(
            context["component_list"], selected_items
        )
        context["steel_pile_table"] = build_component_table(
            context["constn"], table_level, selected_items_map
        )
        context["selected_items"] = selected_items
        return render_to_string("constn_report/component_table.html", context)

    elif table_name == "tool":
        selected_items_map = filter_selected_items(context["tool_list"], selected_items)
        context["steel_pile_table"] = build_tools_table(
            context["constn"], table_level, selected_items_map
        )
        context["selected_items"] = selected_items
        return render_to_string("constn_report/tools_table.html", context)

    return "無效的表格類型"


def steel_brace_view(request):
    # 鋼樁
    context = {}
    table_level = 7
    if request.method == "POST":
        code = request.POST.get("site_code")
        context["constn"] = SiteInfo.get_site_by_code(code)

        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level

        context["steel_pile_table"] = build_steel_brace_table(
            context["constn"], table_level
        )

    context["sitelist"] = get_global_site_json()
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
            item.remark = (
                item.remark.replace("None", "")
                .replace("構台樑", "")
                .replace("修改", "")
                + "修改"
            )
            item.save()
        elif quantity == 0 and unit == 0:
            item.remark = item.remark.replace("None", "").replace("修改", "") + "修改"
            item.is_mid = True
            item.save()
        else:
            item.is_mid = False
            item.quantity = quantity
            item.unit = unit
            item.remark = (
                item.remark.replace("None", "")
                .replace("構台樑", "")
                .replace("修改", "")
                + " 修改"
            )
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
        code = request.POST.get("site_code")
        constn = SiteInfo.get_site_by_code(code)

        context["steel_pile_table"] = build_steel_pile_table(constn)
        context["steel_ng_table"] = build_steel_ng_table(constn)
        context["constn"] = constn
        context["column_count"] = range(2)

    context["sitelist"] = get_global_site_json()
    return render(request, "constn_report/steel_pile.html", context)


def component_view(request):
    # 将查询结果传递给模板
    context = {}
    table_level = 7
    component_list = get_global_component_list()
    selected_items = []
    if request.method == "POST":
        code = request.POST.get("site_code")
        selected_items = request.POST.getlist("selected_items")

        # print(constn_obj.query)
        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level
        selected_items_map = [
            item for item in component_list if str(item["id"]) in selected_items
        ]

        context["constn"] = SiteInfo.get_site_by_code(code)
        context["steel_pile_table"] = build_component_table(
            context["constn"], table_level, selected_items_map
        )

    context["sitelist"] = get_global_site_json()
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
        code = request.POST.get("site_code")
        selected_items = request.POST.getlist("selected_items")

        # print(constn_obj.query)
        get_level_val = request.POST.get("level")
        table_level = int(get_level_val) if get_level_val else table_level
        # 使用字典推導式來過濾 tool_list 中的項目，並建立 id 到 name 的映射
        selected_items_map = [
            item for item in tool_list if str(item["id"]) in selected_items
        ]

        context["constn"] = SiteInfo.get_site_by_code(code)
        context["steel_pile_table"] = build_tools_table(
            context["constn"], table_level, selected_items_map
        )

    context["sitelist"] = get_global_site_json()
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
        code = request.POST.get("site_code")
        context["constn"] = SiteInfo.get_site_by_code(code)
        context["steel_table"], context["components"] = build_constn_diff_view(
            context["constn"]
        )

    context["sitelist"] = get_global_site_json()
    # context["mat_tree"] = mat_tree
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/steel_diff.html", context)


def get_sitelist(request):
    # 查詢資料庫中的資料
    sitelist = get_global_site_json(True)

    # 返回 JSON 資料
    return JsonResponse(sitelist, safe=False)


def export_report_list(request):
    # Fetch the list of reports from the database
    code = request.GET.get("sitecode")
    print(code)
    constn = SiteInfo.get_site_by_code(code)
    output_path = os.path.join(settings.BASE_DIR, "templates", "filled_report.xlsx")

    # Fill the template with dynamic data from the report list
    fill_diff_table_excel(constn, output_path)

    # Serve the file as a download
    response = HttpResponse(
        open(output_path, "rb"),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="filled_report.xlsx"'

    try:
        os.remove(output_path)
        print(f"Temporary file {output_path} deleted.")
    except OSError as e:
        print(f"Error deleting temporary file {output_path}: {e}")
    return response
