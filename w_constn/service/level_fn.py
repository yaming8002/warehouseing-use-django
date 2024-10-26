from decimal import Decimal
from typing import Any, Dict, List
from django.db.models import Max
from django.forms import model_to_dict

from w_constn.models.level_reprot import LevelBrace, LevelComponent, LevelTool
from w_stock.models.site_model import SiteInfo

# 預設支架列表
braces_list = [
    {"id": 358, "name": "H300"},
    {"id": 295, "name": "H350"},
    {"id": 424, "name": "H400"},
    {"id": 170, "name": "H408"},
]
model_dict = {"braces": LevelBrace, "component": LevelComponent, "tool": LevelTool}


def transpose_list_of_lists(input_list: List[List[Any]]) -> List[List[Any]]:
    """
    將列表轉置
    """
    max_length = max(len(row) for row in input_list)  # 確定最大長度
    return [
        [row[i] if i < len(row) else None for row in input_list]
        for i in range(max_length)
    ]


def level_summary_of_lists(input_list: List[List[Any]]) -> List[Dict[str, Decimal]]:
    """
    生成每一層的摘要
    """
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            summary["count"] += (
                item["total_quantity"]
                if "total_quantity" in item.keys()
                else item["quantity"]
            )
            summary["unit"] += (
                item["total_unit"] if "total_unit" in item.keys() else item["unit"]
            )
        level_list.append(summary)
    return level_list


def level_table_build_summary_of_lists(
    input_list: List[List[Any]],
) -> List[Dict[str, Decimal]]:
    """
    生成每一層的摘要
    """
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            summary["count"] += Decimal(item.quantity)
            summary["unit"] += Decimal(item.unit)
        level_list.append(summary)
    return level_list


def level_table_build(
    model_type: str, site: SiteInfo, mat_lst=None
) -> Dict[str, Dict[str, Any]]:
    """
    生成鋼材表
    """
    steel_map = {}
    level = 7
    if model_type not in model_dict.keys():
        raise ValueError("Invalid model type")
    # 選擇模型類型
    model = (
        model_dict.get(model_type)
        .objects.select_related("translog", "material")
        .filter(translog__constn_site=site)
    )

    if not model.exists():
        return None,0

    level = model.aggregate(max_level=Max("level"))["max_level"]
    # 如果 mat_lst 為空，則使用 braces_list
    if not mat_lst:
        mat_lst = braces_list
    print('level',level)

    # 遍歷物料列表
    for material in mat_lst:
        mat_id = material["id"]
        name = material["name"]
        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range((level+1) * 2)]
        # 初始化每一層的交易列表和統計摘要
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        # 查詢所有物料數據
        total_quantity_and_unit = model.filter(material__id=mat_id)
        if not total_quantity_and_unit.exists():
            continue

        for seat in range(level+1):
            site_in = (seat * 2) - 1 if seat > 0 else len(tr_list) - 1
            site_out = (seat * 2) - 2 if seat > 0 else len(tr_list) - 2

            for item in total_quantity_and_unit.filter(level=seat):
                if item.translog.transaction_type == "IN":  # 使用模型屬性
                    tr_list[site_in].append(item)
                    summary["count_in"] += Decimal(item.quantity)
                    summary["unit_in"] += Decimal(item.unit)
                else:
                    tr_list[site_out].append(item)
                    summary["count_out"] += Decimal(item.quantity)
                    summary["unit_out"] += Decimal(item.unit)

        max_length = max(len(tr_list[i]) for i in range(len(tr_list)))

        # 計算摘要
        summary["diff_count"] = summary["count_in"] - summary["count_out"]
        summary["diff_unit"] = summary["unit_in"] - summary["unit_out"]
        summary["max_length"] = max_length + 1


        # 更新 steel_map
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 2
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_table_build_summary_of_lists(tr_list)

    return steel_map ,level
