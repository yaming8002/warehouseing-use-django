from django.core.cache import cache

from stock.models.material_model import Materials
from stock.models.steel_model import SteelReport


def get_global_steel_list(update=False):
    setting = cache.get("get_global_steel_list")

    if update or not setting:
        # 當緩存中沒有資料或需要更新時，從資料庫中撈取
        ids = list(SteelReport.static_column_code.keys())
        materials = Materials.objects.filter(id__in=ids)
        setting = {material.mat_code: f"{material.id}" for material in materials}
        # 將結果緩存起來，設定七天的過期時間
        cache.set(
            "get_global_steel_list", setting, timeout=7 * 24 * 60 * 60
        )  # 七天過期

    return setting


def get_global_done_steel_list(update=False):
    mat_list = [
        "358",
        "352",
        "295",
        "400",
        "424",
        "367",
        "170",
        "193",
        "265",
        "102",
        "18",
        "19",
        "30",
        "31",
        "16",
        "230",
    ]
    setting = cache.get("get_global_done_steel_list")

    if update or not setting:
        # 當緩存中沒有資料或需要更新時，從資料庫中撈取
        materials = Materials.objects.filter(id__in=mat_list)
        setting = {f'{material.mat_code}': f'{material.id}' for material in materials}

        # 將結果緩存起來，設定七天的過期時間
        cache.set(
            "get_global_done_steel_list", setting, timeout=7 * 24 * 60 * 60
        )  # 七天過期

    return setting
