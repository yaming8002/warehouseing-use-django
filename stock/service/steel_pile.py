from decimal import Decimal
from typing import Any, Dict, List

from django.db.models import F, Sum, Case, When, Value, Q
from django.forms import IntegerField, model_to_dict

from stock.models.material_model import Materials
from stock.models.steel_pile_model import SteelPile
from trans.models import TransLog, TransLogDetail
from wcom.templatetags.custom_filters import kg_to_meter

ordering = Case(
    When(material__mat_code="3050", then=Value(1)),
    When(Q(material__mat_code="301") & Q(is_mid=False), then=Value(2)),
    When(Q(material__mat_code="301") & Q(is_mid=True), then=Value(3)),
    When(Q(material__mat_code="351")  & Q(is_mid=False), then=Value(4)),
    When(Q(material__mat_code="351") & Q(is_mid=True), then=Value(5)),
    When(Q(material__mat_code="401") & Q(is_mid=False), then=Value(6)),
    When(Q(material__mat_code="401") & Q(is_mid=True), then=Value(7)),
    default=Value(8),  # 其他值的排序
    output_field=IntegerField(),
)

# 初始化查询所用的字段字典
values_dict = {
    "kp": F("id"),
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

    transdefaullog = SteelPile.objects.filter(translog__in=translog, is_ng=False)
    mat_list = (
        transdefaullog.values_list("material__mat_code", "material__name","is_mid")
        .distinct()  # 排除重复记录
        .order_by(ordering)
    )
    steel_map = {}


    for mat_code, name ,is_mid in mat_list:
        if is_mid:
            name = '構台樑 ' + name
        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range(2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        query = Q(material__mat_code=mat_code , is_mid =is_mid )
        items = transdefaullog.filter(query )
        for item in items:
            if item.translog.transaction_type == "IN":
                tr_list[1].append(item)
                summary["count_in"] += Decimal(item.quantity)
                summary["unit_in"] += Decimal(item.unit)
            else:
                tr_list[0].append(item)
                summary["count_out"] += Decimal(item.quantity)
                summary["unit_out"] += Decimal(item.unit)
        max_length = max(max_length, len(tr_list[0]), len(tr_list[1]))

        summary["diff_count"] = summary["count_out"] - summary["count_in"]
        summary["diff_unit"] = summary["unit_out"] - summary["unit_in"]
        summary["max_length"] = max_length + 1
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 2
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_summary_of_lists(tr_list)
    return steel_map



def build_steel_ng_table(constn) -> Dict[str, Dict[str, any]]:
    translog = TransLog.objects.filter(constn_site=constn)

    transdefaullog = SteelPile.objects.filter(translog__in=translog, is_ng=True)
    mat_list = transdefaullog.values_list(
        "material__mat_code", "material__name"
    ).order_by("material__mat_code")
    steel_map = {}

    for mat_code, name in mat_list:
        steel_map[name] = {}
        tr_list: List[List[Any]] = [[] for _ in range(2)]
        max_length = 0
        summary = {
            "count_in": Decimal(0),
            "unit_in": Decimal(0),
            "count_out": Decimal(0),
            "unit_out": Decimal(0),
        }

        items = transdefaullog.filter(material__mat_code=mat_code)
        for item in items:
            if item.translog.transaction_type == "IN":
                tr_list[1].append(item)
                summary["count_in"] += Decimal(item.quantity)
                summary["unit_in"] += Decimal(item.unit)
            else:
                tr_list[0].append(item)
                summary["count_out"] += Decimal(item.quantity)
                summary["unit_out"] +=  Decimal(item.unit)
        max_length = max(max_length, len(tr_list[0]), len(tr_list[1]))

        summary["max_length"] = max_length + 1
        steel_map[name]["mat_code"] = mat_code
        steel_map[name]["summary"] = summary
        steel_map[name]["max_length"] = max_length + 2
        steel_map[name]["table"] = transpose_list_of_lists(tr_list)
        steel_map[name]["level_summary"] = level_ng_summary_of_lists(tr_list)
    return steel_map


def level_summary_of_lists(input_list):
    # 确定最大长度
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            summary["count"] += item.quantity
            summary["unit"] += item.unit
        level_list.append(summary)

    # print(level_list)
    return level_list

def level_ng_summary_of_lists(input_list):
    # 确定最大长度
    level_list: List[Dict[str, Decimal]] = []
    for row in input_list:
        summary = {"count": Decimal(0), "unit": Decimal(0)}
        for item in row:
            mat_code = item.material.mat_code
            summary["count"] += item.quantity
            summary["unit"] += Decimal( kg_to_meter(mat_code, Decimal(item.quantity)))
        level_list.append(summary)

    # print(level_list)
    return level_list

def transpose_list_of_lists(input_list):
    # 确定最大长度
    max_length = max(len(row) for row in input_list)

    # 创建转置后的列表
    transposed_list = []
    for i in range(max_length):
        transposed_row = [row[i] if i < len(row) else None for row in input_list]
        transposed_list.append(transposed_row)

    return transposed_list
