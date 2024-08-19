
from django.core.cache import cache

from stock.models.material_model import Materials


def get_global_tool_list(update =False):
    setting = cache.get('global_tool_list')
    if  update or not setting:
        # 當緩存中沒有資料時，從資料庫中撈取
        setting = Materials.objects.values('id','name').filter(tool_report = True).order_by('name')
        # 將撈取到的資料存入緩存，並設置過期時間
        cache.set('global_tool_list', setting, timeout=7*24*60*60)  # 七天過期
    return setting

def get_global_component_list(update =False):
    setting = cache.get('global_component_list')
    if  update or not setting:
        # 當緩存中沒有資料時，從資料庫中撈取
        setting = Materials.objects.values('id','name','component').filter(component__gt=0).order_by('component','name')
        # 將撈取到的資料存入緩存，並設置過期時間
        cache.set('global_component_list', setting, timeout=7*24*60*60)  # 七天過期
    return setting
