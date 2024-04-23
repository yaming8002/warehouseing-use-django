from django.shortcuts import render

from stock.util.steel_brace import build_steel_brace_table
from stock.util.steel_pile import build_steel_ng_table
from stock.util.steel_component import component_map, build_component_table
from stock.models.site_model import SiteInfo
from wcommon.templatetags.strmap import get_level

# Create your views here.


def steel_brace_view(request):
    # 将查询结果传递给模板
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
            # context["steel_pile_table"] = build_steel_pile_table(constn.get())
            context["steel_ng_table"] = build_steel_ng_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(2)

    return render(request, "constn_report/steel_pile.html", context)


def component_view(request):
    # 将查询结果传递给模板
    context = {}
    table_level = 7
    selected_items = []
    if request.method == "GET":
        owner = request.GET.get("owner")
        code = request.GET.get("code")
        name = request.GET.get("name")
        selected_items = request.GET.getlist("selected_items")

        print("selected_items", selected_items)
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

        selected_items_map = {key: component_map[key] for key in selected_items}
        print(selected_items_map)
        if show and constn.exists():
            context["steel_pile_table"] = build_component_table(
                constn.get(), table_level, selected_items_map
            )
            print(context["steel_pile_table"])
            context["constn"] = constn.get()

            context["select_level"] = [x for x in get_level() if (x[0] > 0)]

    context["mat_tree"] = mat_tree
    context["selected_items"] = selected_items
    context["table_level"] = table_level
    context["column_count"] = range(table_level * 2)
    return render(request, "constn_report/component.html", context)


mat_tree = [
    {
        "topic": "main",
        "name": "主要",
        "mat_list": [
            {"key": "10", "value": "補強板(接樁用)"},
            {"key": "6300", "value": "H300止水板"},
            {"key": "6350", "value": "H350止水板"},
            {"key": "6400", "value": "H400止水板"},
            {"key": "79", "value": "擋土板5.6.8分"},
            {"key": "44", "value": "黑皮"},
            {"key": "9", "value": "防墬網/安全網"},
            {"key": "11", "value": "覆工板 1M *2M"},
            {"key": "12", "value": "洗車版 2M *2M"},
            {"key": "2105", "value": "鋪路鐵板 半"},
            {"key": "21", "value": "鋪路鐵板 全"},
            {"key": "13", "value": "千斤頂"},
            {"key": "14", "value": "土壓計"},
            {"key": "16", "value": "樓梯"},
            {"key": "19", "value": "樓梯鐵板0.8*1.5M"},
            {"key": "20", "value": "樓梯鐵板 1*1 / 1*2"},
            {"key": "2201", "value": "斜撐 H250.300"},
            {"key": "2202", "value": "斜撐 H350"},
            {"key": "4285", "value": "H428斜撐"},
            {"key": "18", "value": "安全步道"},
        ],
    },
    {
        "topic": "tool",
        "name": "工具",
        "mat_list": [
            {"key": "47", "value": "風車 大 / 小"},
            {"key": "55", "value": "發電機(悍馬電焊)"},
            {"key": "561", "value": "發電機(90P)"},
            {"key": "562", "value": "發電機(150P)"},
            {"key": "57", "value": "雙用丫頭(鑽)"},
            {"key": "58", "value": "單用小丫頭(破)"},
            {"key": "59", "value": "大丫頭(破碎機)"},
            {"key": "63", "value": "手推車(乙炔車)"},
            {"key": "64", "value": "滅火器"},
            {"key": "62", "value": "切斷器"},
            {"key": "41", "value": "吊桶 / 混擬土桶"},
            {"key": "48", "value": "風槍(打螺絲)"},
            {"key": "751", "value": "電動槍 大"},
            {"key": "752", "value": "電動槍 小"},
            {"key": "61", "value": "110V電線"},
        ],
    },
    {
        "topic": "other",
        "name": "其他",
        "mat_list": [
            {"key": "23", "value": "牛頭粒"},
            {"key": "26", "value": "活動頭"},
            {"key": "92", "value": "獅子頭"},
            {"key": "93", "value": "老虎頭"},
            {"key": "94", "value": "鯊魚頭"},
            {"key": "97", "value": "小象頭"},
            {"key": "95", "value": "新式擋頭(小丫嘴頭)"},
            {"key": "24", "value": "鋼軌三角架"},
            {"key": "27", "value": "H大三角架"},
            {"key": "28", "value": "H小三角架"},
            {"key": "8", "value": "H短接(1M以下)"},
            {"key": "5", "value": '7/8"螺絲 長'},
            {"key": "6", "value": '7/8"螺絲 短'},
            {"key": "25", "value": "大 / 小 魚鉤螺絲"},
            {"key": "46", "value": "膨脹螺絲(壁虎)"},
            {"key": "85", "value": "伸縮鋁梯"},
            {"key": "2300", "value": "H300 大U型螺絲"},
            {"key": "2350", "value": "H350 大U型螺絲"},
            {"key": "2400", "value": "H400 大U型螺絲"},
            {"key": "4141", "value": "H414大U"},
            {"key": "4281", "value": "H428大U"},
            {"key": "3300", "value": "H300 小U型螺絲"},
            {"key": "3350", "value": "H350 小U型螺絲"},
            {"key": "3400", "value": "H400 小U型螺絲"},
            {"key": "4142", "value": "H414小U"},
            {"key": "4282", "value": "H428小U"},
            {"key": "4", "value": "U型螺絲角鐵"},
            {"key": "4280", "value": "H428合板"},
            {"key": "1300", "value": "H300 合 板"},
            {"key": "1350", "value": "H350 合 板"},
            {"key": "1400", "value": "H400 合 板"},
            {"key": "230", "value": "圍苓加勁盒(便當盒)"},
            {"key": "15", "value": "保護夾"},
            {"key": "33", "value": "GIP管 L:6M"},
            {"key": "32", "value": "GIP管立柱: 1.2 M"},
            {"key": "31", "value": "GIP管 L:"},
            {"key": "30", "value": "構台帽 H350.H400"},
            {"key": "7", "value": "背填(C型夾砲管)"},
            {"key": "34", "value": "活扣"},
        ],
    },
]
