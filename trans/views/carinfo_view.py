from datetime import date
from decimal import Decimal
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from datetime import datetime, timedelta
from stock.models.site import SiteInfo
from trans.forms import CarinfoFrom
from trans.models import CarInfo

from wcommon.utils.excel_tool import ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from stock.models.material import MatCat, Materials, MatSpec
from wcommon.utils.save_control import SaveControlView
from wcommon.utils.uitls import excel_value_to_str


class CarListView(PageListView):
    model = CarInfo
    template_name = "trans/carinfo.html"
    title_name = "車輛清單"

    def get_queryset(self):
        result = CarInfo.objects
        car_number = self.request.GET.get("car_number")
        firm = self.request.GET.get("firm")

        group = self.request.GET.get("group")
        if car_number:
            result = result.filter(car_number__istartswith=car_number)
        if group :
            result = result.filter(is_count=(group=='1'))
        elif firm:
            result = result.filter(firm__startswith=firm)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CarInfoControlView(SaveControlView):
    name = "車輛資訊"
    model = CarInfo
    form_class = CarinfoFrom


class ImportCarInfoView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/carinfo/uploadexcel/"
    columns = ["車牌號碼",  "吊卡車公司", "噸數(備註)", "基本台金"]

    def insertDB(self, actual_columns):
        for item in actual_columns:
            if item[0] is None:
                break
            code = excel_value_to_str(item[0])
            firm = item[1]
            
            try:
                if CarInfo.objects.filter(car_number=code, firm=firm).exists():
                    print(f"{code},{firm} is exists")
                else :
                    CarInfo.create(
                        car_number=code,
                        firm= firm,
                        remark=item[2],
                        value=item[3],
                    )   
            except Exception as e:
                # 处理可能的异常情况
                print(f"{item} insertDB An error occurred:{e}")
                self.error_list.append((item, '資料異常'))