import decimal
import math
from decimal import Decimal
from typing import Dict, List, Any

from django.db.models import F, Sum
from django.shortcuts import render

from stock.models.material_model import Materials
from stock.models.site_model import SiteInfo
from trans.models import TransLogDetail, TransLog

support_list = {"300": "H300", "350": "H350", "400": "H400", "408": "H408"}
values_dict = {
    "code": F("translog__code"),
    "build_date": F("translog__build_date"),
    "transaction_type": F("translog__transaction_type"),
    "name": F("material__name"),
    "level_annotation": F("level"),
}

def build_steel_brace_table(constn,level) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)
    mats = Materials.objects.filter(specification__lt=23)
    transdefaullog = TransLogDetail.objects.filter(
        translog__in=translog, material__in=mats
    )

    steel_map = {}
    
    for mat_code, name in support_list.items():
        # name = f"m_{mat_code}"
        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range(level*2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }
        print(level)
        
        for seat in range(level):
            print(f"seat{seat}")
            total_quantity_and_unit = (
                transdefaullog.filter(material__mat_code=mat_code, level=(seat + 1))
                .values(
                    code=F("translog__code"),  # 将物流编号包含在结果中
                    build_date=F("translog__build_date"),  # 将物流建立日期包含在结果中
                    transaction_type=F(
                        "translog__transaction_type"
                    ),  # 将物流交易类型包含在结果中
                    name=F("material__name"),  # 将物流交易类型包含在结果中
                    level_annotation=F("level"),
                )
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
                    summary["unit_in"] += Decimal(item["total_unit"])
                else:
                    tr_list[site_out].append(item)
                    summary["count_out"] += Decimal(item["total_quantity"])
                    summary["unit_out"] += Decimal(item["total_unit"])
            max_length = max(max_length, len(tr_list[site_in]), len(tr_list[site_out]))

        summary["diff_count"] = summary["count_in"] - summary["count_out"]
        summary["diff_unit"] = summary["unit_in"] - summary["unit_out"]
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
    print(input_list)
    # 创建转置后的列表
    transposed_list = []
    for i in range(max_length):
        transposed_row = []
        for row in input_list:
            if i < len(row):
                transposed_row.append(row[i])
            else:
                transposed_row.append(None)
        transposed_list.append(transposed_row)

    return transposed_list


def level_summary_of_lists(input_list):
    # 确定最大长度
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            summary["count"] += item["total_quantity"]
            summary["unit"] += item["total_unit"]
        level_list.append(summary)

    # print(level_list)
    return level_list
