from decimal import Decimal
from typing import Any, Dict, List

from django.db.models import F, Sum

from stock.models.material_model import Materials
from trans.models import TransLog, TransLogDetail

support_list = {
    "3050-0": "鋼軌樁",
    "301-0": "中\nH300",
    "301-1": "中\nH300構台樑",
    "351-0": "中\nH350",
    "351-1": "中\nH350構台樑",
    "401-0": "中\nH400",
    "401-1": "中\nH400構台樑",
}
# 初始化查询所用的字段字典
values_dict = {
    "code": F("translog__code"),
    "build_date": F("translog__build_date"),
    "transaction_type": F("translog__transaction_type"),
    "turn_site": F("translog__turn_site__code"),
    "name": F("material__name"),
    "level_annotation": F("level"),
    "d_remark": F("remark"),
}


def build_steel_pile_table(constn) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)
    mats = Materials.objects.filter(specification__lt=23)
    transdefaullog = TransLogDetail.objects.filter(
        translog__in=translog, material__in=mats
    )

    steel_map = {}
    for key, name in support_list.items():
        # name = f"m_{mat_code}"
        mat_code = key.split("-")[0]
        construct_case = key.split("-")[1] == "1"

        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range(2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        # 根据条件动态构建查询
        if construct_case:
            # 选择remark为"中構台"的项目
            queryset = transdefaullog.filter(
                material__mat_code=mat_code, remark__icontains="構台樑"
            )
        else:
            # 选择remark不为"中構台"的项目
            queryset = transdefaullog.filter(material__mat_code=mat_code).exclude(
                remark__icontains="構台樑"
            )

        total_quantity_and_unit = queryset.values(**values_dict).annotate(
            total_quantity=Sum("quantity"),
            total_unit=Sum("all_unit"),
        )

        for item in total_quantity_and_unit:
            # print(item)
            if item["transaction_type"] == "IN":
                tr_list[1].append(item)
                summary["count_in"] += Decimal(item["total_quantity"])
                summary["unit_in"] += Decimal(item["total_unit"])
            else:
                tr_list[0].append(item)
                summary["count_out"] += Decimal(item["total_quantity"])
                summary["unit_out"] += Decimal(item["total_unit"])
        max_length = max(max_length, len(tr_list[0]), len(tr_list[1]))

        summary["diff_count"] = summary["count_in"] - summary["count_out"]
        summary["diff_unit"] = summary["unit_in"] - summary["unit_out"]
        summary["max_length"] = max_length + 1
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 2
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_summary_of_lists(tr_list)
    return steel_map


steel_ng_map = {26:("300","H300"), 27: ("350","H350"), 28: ("400","H400"), 25: ("3050","鋼軌")}


def build_steel_ng_table(constn) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)
    mats = Materials.objects.filter(mat_code=999)
    transdefaullog = TransLogDetail.objects.filter(
        translog__in=translog, material__in=mats
    )

    steel_map = {}
    for key, name in steel_ng_map.items():
        # name = f"m_{mat_code}"
        steel_map[name[1]] = {}
        tr_list: List[List[Any]] = [[] for _ in range(2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        queryset = transdefaullog.filter(material__specification=key)

        total_quantity_and_unit = queryset.values(**values_dict).annotate(
            total_quantity=Sum("quantity"),
            total_unit=Sum("all_unit"),
        )

        for item in total_quantity_and_unit:
            # print(item)
            if item["transaction_type"] == "IN":
                tr_list[1].append(item)
                summary["count_in"] += Decimal(item["total_quantity"])
                summary["unit_in"] += Decimal(item["total_unit"])
            else:
                tr_list[0].append(item)
                summary["count_out"] += Decimal(item["total_quantity"])
                summary["unit_out"] += Decimal(item["total_unit"])
        max_length = max(max_length, len(tr_list[0]), len(tr_list[1]))

        summary["max_length"] = max_length + 1
        steel_map[name[1]]["mat_code"] = name[0]
        steel_map[name[1]]["summary"] = summary
        steel_map[name[1]]["max_length"] = max_length + 2
        steel_map[name[1]]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name[1]]["level_summary"] = level_summary_of_lists(tr_list)
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
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            summary["count"] += item["total_quantity"]
            summary["unit"] += item["total_unit"]
        level_list.append(summary)

    # print(level_list)
    return level_list
