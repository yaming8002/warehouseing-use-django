from datetime import datetime
from django.forms import model_to_dict
from django.test import TestCase

from stock.models.material_model import MatSpec
from trans.models.trans_model import TransLog, TransLogDetail
from wcom.models.menu import SysInfo
from wcom.utils.uitls import excel_num_to_date, excel_value_to_str

# Create your tests here.
 # [None, 45502, 1682, None, '億東營造', '新北市三重區仁政街57號(龍昊三重)', 'C035460', 999, 'NG/廢鐵', None, '', 110, None, 0, 0, 110, 0, 0, 0, 0, '廢鐵', 11, '第一層入料', '國廣', 6306, 18, '羅浚升', 45506],
 # 'e': 'Materials matching query does not exist.\nDoesNotExist\nTraceback (most recent call last):\n  File "/app/trans/views/transportlog_view.py", line 203, in insertDB\n    detail = TransLogDetail.create(trans_log, item, is_rent=False)\n  File "/app/trans/models/trans_model.py", line 133, in create\n    mat = Materials.get_item_by_code(mat_code, remark, unit)\n  File "/app/stock/models/material_model.py", line 66, in get_item_by_code\n    return cls.objects.get(quest)\n  File "/usr/local/lib/python3.10/site-packages/django/db/models/manager.py", line 87, in manager_method\n    return getattr(self.get_queryset(), name)(*args, **kwargs)\n  File "/usr/local/lib/python3.10/site-packages/django/db/models/query.py", line 647, in get\n    raise self.model.DoesNotExist(\nstock.models.material_model.Materials.DoesNotExist: Materials matching query does not exist.\n'}

class MyViewTestCase(TestCase):

    def test_model_creation(self):
        # trans_end_date = SysInfo.get_value_by_name("trans_end_day")
        trans_end_date = datetime.strptime('2024/7/14', "%Y/%m/%d")
        end_date = trans_end_date
        trans_log_details = []
        item = [None, 45502, 1682, None, '億東營造', '新北市三重區仁政街57號(龍昊三重)', 'C035460', 999, 'NG/廢鐵', None, '', 110, None, 0, 0, 110, 0, 0, 0, 0, '廢鐵', 11, '第一層入料', '國廣', 6306, 18, '羅浚升', 45506]
        trancode = excel_value_to_str(item[6])
        if trancode is None:
            return

        mat_code = excel_value_to_str(item[8])
        edit_date = excel_num_to_date(item[27])

        end_date = (
            end_date if end_date > edit_date else edit_date
        )
        remark = excel_value_to_str(item[20])


        trans_log = None
        if mat_code and mat_code != "":
            detail = TransLogDetail.create(trans_log, item, is_rent=False)
        print(detail)
