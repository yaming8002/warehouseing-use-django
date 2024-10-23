from decimal import Decimal
from typing import Dict, List


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
