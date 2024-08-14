import decimal
import math
from decimal import Decimal
from typing import Any, Dict, List
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Q, F, Sum, Value, When
from django.shortcuts import render

from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from trans.models import TransLog, TransLogDetail

component_map = {
    "100": "補強板(接樁用)",
    "6300": "H300止水板",
    "6350": "H350止水板",
    "6400": "H400止水板",
    "-": "擋土板5.6.8分",
    "44":"黑皮",
    "11": "防墬網/安全網",
    "92": "覆工板 1M *2M",
    "95": "洗車版 2M *2M",
    "2205": "鋪路鐵板 半",
    "22": "鋪路鐵板 全",
    "12": "千斤頂",
    "13": "土壓計",
    "15": "樓梯",
    "122": "樓梯鐵板0.8*1.5M",
    "21": "樓梯鐵板 1*1 / 1*2",
    "2301": "斜撐 H250.300",
    "2302": "斜撐 H350",
    "4285": "H428斜撐",
    "18": "安全步道",
    "17": "伸縮鋁梯",
    "91": "伸縮臂",
    "24": "牛頭粒",
    "81": "牛擔頭",
    "25": "活動頭",
    "83": "角嶼(角斗)",
    "82": "豹子頭",
    "78": "獅子頭",
    "79": "老虎頭",
    "80": "鯊魚頭",
    "55": "雙用丫頭(鑽)",
    "56": "單用小丫頭(破)",
    "75": "大象頭",
    "76": "小象頭",
    "---" : "中象頭",
    "48" : "鋼索 30M",
    "49" : "鋼索夾",
    "29": "鋼軌三角架",
    "30": "H大三角架",
    "31": "H小三角架",
    "10": "H短接(1M以下)",
    "5": '7/8"螺絲 長',
    "6": '7/8"螺絲 短',
    "77": "新式擋頭(小丫嘴頭)",
    "8": "大 / 小 魚鉤螺絲",
    "7": "膨脹螺絲(壁虎)",
    "2300": "H300 大U型螺絲",
    "2350": "H350 大U型螺絲",
    "2400": "H400 大U型螺絲",
    "4141": "H414大U",
    "4281": "H428大U",
    "3300": "H300 小U型螺絲",
    "3350": "H350 小U型螺絲",
    "3400": "H400 小U型螺絲",
    "4142": "H414小U",
    "4282": "H428小U",
    "4": "U型螺絲角鐵",
    "4280": "H428合板",
    "1300": "H300 合 板",
    "1350": "H350 合 板",
    "1400": "H400 合 板",
    "26": "圍苓加勁盒(便當盒)",
    "14": "保護夾",
    "36": "GIP管 L:6M",
    "35": "GIP管立柱: 1.2 M",
    "34": "GIP管 L:",
    "27": "構台帽 H350.H400",
    "9": "背填(C型夾砲管)",
    "37": "活扣",
    "50": "風車 大 / 小",
    "28": "發電機(悍馬電焊)",
    "89": "發電機(90P)",
    "90": "發電機(150P)",
    "561": "大丫頭(破碎機)",
    "60": "手推車(乙炔車)",
    "61": "滅火器",
    "59": "切斷器",
    "45": "吊桶 / 混擬土桶",
    "51": "風槍(打螺絲)",
    "71": "電動槍  大 / 強",
    "--": "電動槍 小",
    "58": "110V電線",
}



mat_tree = [
    {
        "topic": "main",
        "name": "主要",
        "mat_list": [
            {"key": "100", "value": "補強板(接樁用)"},
            {"key": "6300", "value": "H300止水板"},
            {"key": "6350", "value": "H350止水板"},
            {"key": "6400", "value": "H400止水板"},
            {"key": "-", "value": "擋土板5.6.8分"},
            {"key": "44", "value": "黑皮"},
            {"key": "11", "value": "防墬網/安全網"},
            {"key": "92", "value": "覆工板 1M *2M"},
            {"key": "95", "value": "洗車版 2M *2M"},
            {"key": "2205", "value": "鋪路鐵板 半"},
            {"key": "22", "value": "鋪路鐵板 全"},
            {"key": "12", "value": "千斤頂"},
            {"key": "13", "value": "土壓計"},
            {"key": "15", "value": "樓梯"},
            {"key": "122", "value": "樓梯鐵板0.8*1.5M"},
            {"key": "21", "value": "樓梯鐵板 1*1 / 1*2"},
            {"key": "2301", "value": "斜撐 H250.300"},
            {"key": "2302", "value": "斜撐 H350"},
            {"key": "4285", "value": "H428斜撐"},
            {"key": "18", "value": "安全步道"},
        ],
    },
    {
        "topic": "tool",
        "name": "工具",
        "mat_list": [
            {"key": "50", "value": "風車 大 / 小"},
            {"key": "28", "value": "發電機(悍馬電焊)"},
            {"key": "89", "value": "發電機(90P)"},
            {"key": "90", "value": "發電機(150P)"},
            {"key": "55", "value": "雙用丫頭(鑽)"},
            {"key": "56", "value": "單用小丫頭(破)"},
            {"key": "561", "value": "大丫頭(破碎機)"},
            {"key": "60", "value": "手推車(乙炔車)"},
            {"key": "61", "value": "滅火器"},
            {"key": "59", "value": "切斷器"},
            {"key": "45", "value": "吊桶 / 混擬土桶"},
            {"key": "51", "value": "風槍(打螺絲)"},
            {"key": "71", "value": "電動槍  大 / 強"},
            {"key": "--", "value": "電動槍 小"},
            {"key": "58", "value": "110V電線"},
        ],
    },
    {
        "topic": "other",
        "name": "其他",
        "mat_list": [
            {"key": "17", "value": "伸縮鋁梯"},
            {"key": "91", "value": "伸縮臂"},
            {"key": "24", "value": "牛頭粒"},
            {"key": "81", "value": "牛擔頭"},
            {"key": "25", "value": "活動頭"},

            {"key": "78", "value": "獅子頭"},
            {"key": "79", "value": "老虎頭"},
            {"key": "80", "value": "鯊魚頭"},
            {"key": "76", "value": "小象頭"},
            {"key": "77", "value": "新式擋頭(小丫嘴頭)"},
            {"key": "29", "value": "鋼軌三角架"},
            {"key": "30", "value": "H大三角架"},
            {"key": "31", "value": "H小三角架"},
            {"key": "10", "value": "H短接(1M以下)"},
            {"key": "5", "value": '7/8"螺絲 長'},
            {"key": "6", "value": '7/8"螺絲 短'},
            {"key": "8", "value": "大 / 小 魚鉤螺絲"},
            {"key": "7", "value": "膨脹螺絲(壁虎)"},
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
            {"key": "26", "value": "圍苓加勁盒(便當盒)"},
            {"key": "14", "value": "保護夾"},
            {"key": "36", "value": "GIP管 L:6M"},
            {"key": "35", "value": "GIP管立柱: 1.2 M"},
            {"key": "34", "value": "GIP管 L:"},
            {"key": "27", "value": "構台帽 H350.H400"},
            {"key": "9", "value": "背填(C型夾砲管)"},
            {"key": "37", "value": "活扣"},
        ],
    },
]

# 初始化查询所用的字段字典
values_dict = {
    "code": F("translog__code"),
    "build_date": F("translog__build_date"),
    "transaction_type": F("translog__transaction_type"),
    "name": F("material__name"),
    "level_annotation": F("level"),
}


def build_component_table(constn, level, map_list) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)
    transdefaullog = TransLogDetail.objects.filter(translog__in=translog)

    steel_map = dict()
    level +=1
    for mat_code, name in map_list.items():
        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range(level * 2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        for seat in range(level):
            query= Q(material__mat_code=mat_code)
            if seat==0:
                query &= (Q(level = seat) | Q(level__isnull=True) )
            else:
                query &= Q(level = seat)

            total_quantity_and_unit = (
                transdefaullog.filter(query)
                .values(**values_dict)
                .annotate(
                    total_quantity=Sum("quantity"),
                    total_unit=Sum("all_unit"),
                )
            )

            if seat == 0:
                site_in = len(tr_list)-1
                site_out = len(tr_list)-2
            else:
                site_in = (seat * 2) - 1
                site_out = (seat * 2) - 2
            for item in total_quantity_and_unit:
                # print(item)
                if item["transaction_type"] == "IN":
                    tr_list[site_in].append(item)
                    summary["count_in"] += Decimal(item["total_quantity"])
                else:
                    tr_list[site_out].append(item)
                    summary["count_out"] += Decimal(item["total_quantity"])

            max_length = max(max_length, len(tr_list[site_in]), len(tr_list[site_out]))

        summary["diff_count"] = summary["count_in"] - summary["count_out"]
        summary["max_length"] = max_length +1
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 1
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_summary_of_lists(tr_list)

    return steel_map


def transpose_list_of_lists(input_list):
    # 确定最大长度
    max_length = max(len(row) for row in input_list)
    # 创建转置后的列表
    transposed_list = []
    for i in range(max_length):
        transposed_row = [row[i] if i < len(row) else None for row in input_list]
        transposed_list.append(transposed_row)

    return transposed_list


def level_summary_of_lists(input_list):
    # 确定最大长度
    level_list = []
    for row in input_list:
        summary = sum([item["total_quantity"] for item in row ])
        level_list.append(summary)

    # print(level_list)
    return level_list
