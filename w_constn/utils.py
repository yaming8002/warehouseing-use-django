from datetime import datetime
import os
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from openpyxl import load_workbook
from w_constn.service.steel_diff_summary import build_constn_diff_view
from w_trans.models.trans_model import TransLog
from wcom.utils.uitls import to_taiwan_date_format

def fill_diff_table_excel(constn, output_path):
    # 差異表的EXCEL 匯出
    steel_table, components = build_constn_diff_view(constn)

    # Define the path to the template and output
    template_path = os.path.join(settings.BASE_DIR, "static", "差異表_模板.xlsx")
    workbook = load_workbook(template_path)
    sheet = workbook.active
    first_record = (
        TransLog.objects.values("build_date")
        .filter(constn_site=constn)
        .order_by("build_date")
        .first()
    )
    last_record = (
        TransLog.objects.values("build_date")
        .filter(constn_site=constn)
        .order_by("build_date")
        .last()
    )
    map = {
        "date": to_taiwan_date_format(datetime.now()),
        "begin": to_taiwan_date_format(first_record["build_date"]),
        "end": to_taiwan_date_format(last_record["build_date"]),
        "code": constn.code,
        "owner": constn.owner,
        "name": constn.name,
    }
    replace_cell_value(sheet, map, row_size=5)

    current_row = 9
    for report in steel_table:
        # Insert data for each report into the corresponding columns
        sheet[f"I{current_row}"] = report["input"]["quantity"]
        sheet[f"J{current_row}"] = report["input"]["unit"]
        sheet[f"K{current_row}"] = report["output"]["quantity"]
        sheet[f"L{current_row}"] = report["output"]["unit"]
        sheet[f"M{current_row}"] = report["ng_value"]
        current_row += 1
    # Assuming the first row is the header, start adding data from the second row
    current_row += 2  # Start after the header
    for report in components:
        # Insert data for each report into the corresponding columns
        sheet[f"I{current_row}"] = report["input"]["quantity"]
        sheet[f"K{current_row}"] = report["output"]["quantity"]
        current_row += 1

    # Save the updated Excel file
    workbook.save(output_path)


def replace_cell_value(sheet, map: dict, row_size=5):
    currect_row = 0
    for row in sheet.iter_rows():
        if currect_row > row_size:
            break
        for cell in row:
            for x in map.keys():
                target = "{" + x + "}"
                if cell.value and isinstance(cell.value, str) and target in cell.value:
                    cell.value = cell.value.replace(target, map[x])

        currect_row += 1

def filter_selected_items(item_list, selected_items):
    """過濾所選項目並返回對應的項目映射"""
    return [item for item in item_list if str(item["id"]) in selected_items]

def filter_selected_mat_items(item_list, selected_items):
    """過濾所選項目並返回對應的項目映射"""
    return [item for item in item_list if str(item["id"]) in selected_items]

def get_table_level(level_str):
    """將 level 字符串轉換為整數，或返回默認值"""
    try:
        return int(level_str) if level_str else 7
    except ValueError:
        return 7
