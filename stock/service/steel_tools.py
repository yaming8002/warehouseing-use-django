from decimal import Decimal
from typing import Any, Dict, List

from django.db.models import F, Q, Sum

from trans.models import TransLog, TransLogDetail

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


def build_tools_table(constn, level, map_list) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)
    transdefaullog = TransLogDetail.objects.filter(translog__in=translog)
    print(map_list)
    steel_map = dict()
    level += 1
    for tool in map_list:
        id = tool["id"]
        name = tool["name"]
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
            query = Q(material__id=id)
            if seat == 0:
                query &= Q(level=seat) | Q(level__isnull=True)
            else:
                query &= Q(level=seat)

            total_quantity_and_unit = (
                transdefaullog.filter(query)
                .values(**values_dict)
                .annotate(
                    total_quantity=Sum("quantity"),
                    total_unit=Sum("all_unit"),
                )
            )

            if seat == 0:
                site_in = len(tr_list) - 1
                site_out = len(tr_list) - 2
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
        summary["max_length"] = max_length + 1
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
        summary = sum([item["total_quantity"] for item in row])
        level_list.append(summary)

    # print(level_list)
    return level_list
