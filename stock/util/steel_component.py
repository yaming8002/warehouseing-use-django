import decimal
import math
from decimal import Decimal
from typing import Any, Dict, List
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Case, F, Sum, Value, When
from django.shortcuts import render

from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from trans.models import TransLog, TransLogDetail

component_map = {
    "10": "補強板(接樁用)",
    "6300": "H300止水板",
    "6350": "H350止水板",
    "6400": "H400止水板",
    "79": "擋土板5.6.8分",
    "44":"黑皮",
    "9": "防墬網/安全網",
    "11": "覆工板 1M *2M",
    "12": "洗車版 2M *2M",
    "2105": "鋪路鐵板 半",
    "21": "鋪路鐵板 全",
    "13": "千斤頂",
    "14": "土壓計",
    "16": "樓梯",
    "19": "樓梯鐵板0.8*1.5M",
    "20": "樓梯鐵板 1*1 / 1*2",
    "2201": "斜撐 H250.300",
    "2202": "斜撐 H350",
    "4285": "H428斜撐",
    "18": "安全步道",
    "23": "牛頭粒",
    "26": "活動頭",
    "92": "獅子頭",
    "93": "老虎頭",
    "94": "鯊魚頭",
    "97": "小象頭",
    "95": "新式擋頭(小丫嘴頭)",
    "24": "鋼軌三角架",
    "27": "H大三角架",
    "28": "H小三角架",
    "8": "H短接(1M以下)",
    "5": '7/8"螺絲 長',
    "6": '7/8"螺絲 短',
    "25": "大 / 小 魚鉤螺絲",
    "46": "膨脹螺絲(壁虎)",
    "85": "伸縮鋁梯",
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
    "230": "圍苓加勁盒(便當盒)",
    "15": "保護夾",
    "33": "GIP管 L:6M",
    "32": "GIP管立柱: 1.2 M",
    "31": "GIP管 L:",
    "30": "構台帽 H350.H400",
    "7": "背填(C型夾砲管)",
    "34": "活扣",
    "47": "風車 大 / 小",
    "55": "發電機(悍馬電焊)",
    "561": "發電機(90P)",
    "562": "發電機(150P)",
    "57": "雙用丫頭(鑽)",
    "58": "單用小丫頭(破)",
    "59": "大丫頭(破碎機)",
    "63": "手推車(乙炔車)",
    "64": "滅火器",
    "62": "切斷器",
    "41": "吊桶 / 混擬土桶",
    "48": "風槍(打螺絲)",
    "751": "電動槍 大",
    "752": "電動槍 小",
    "61": "110V電線",
}

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
            print(
                transdefaullog.filter(
                    material__mat_code=mat_code, level=(seat + 1)
                ).query
            )
            total_quantity_and_unit = (
                transdefaullog.filter(material__mat_code=mat_code, level=(seat + 1))
                .values(**values_dict)
                .annotate(
                    total_quantity=Sum("quantity"),
                    total_unit=Sum("all_unit"),
                )
            )

            site_in = (seat * 2) + 1
            site_out = seat * 2
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
        summary["max_length"] = max_length + 1
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 2
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_summary_of_lists(tr_list)
        # print(steel_map[name]["table"] )
        # print(f"name:{name},max:{max_length}")
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
