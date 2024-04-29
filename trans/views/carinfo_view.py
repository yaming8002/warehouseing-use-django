from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from stock.models.material_model import MatCat, Materials, MatSpec
from stock.models.site_model import SiteInfo
from trans.forms import CarinfoFrom
from trans.models import CarInfo
from wcommon.utils.excel_tool import ImportData2Generic, ImportDataGeneric
from wcommon.utils.pagelist import PageListView
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
        if group:
            result = result.filter(is_count=(group == "1"))
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

    def form_is_valid(self ,form):
        form.instance.is_count = form.cleaned_data.get('is_count', False)



class ImportCarInfoView(ImportData2Generic):
    title = "上傳EXCEL"
    action = "/carinfo/uploadexcel/"
    columns = ["車牌號碼", "吊卡車公司", "噸數(備註)", "基本台金"]

    def insertDB(self, item):
        if item[0] is None:
            return 
        code = excel_value_to_str(item[0])
        firm = item[1]
        
        if CarInfo.objects.filter(car_number=code, firm=firm).exists():
            print(f"{code},{firm} is exists")
        else:
            CarInfo.create(
                car_number=code,
                firm=firm,
                remark=item[2],
                value=item[3],
            )


class ImportCarInfoByTotalView(ImportData2Generic):
    def insertDB(self, item):
        if  "car_number" not in item.keys() :
            return
        remark = f"{item['remark']}" if "remark" in item.keys() else ""
        remark += f",{item['value']}" if "value" in item.keys() else ""

        if CarInfo.objects.filter(car_number=item['car_number']).exists():
            CarInfo.objects.filter(car_number=item['car_number']).update(
                firm=item['car_firm'],
                remark=remark
            )
        else :
            CarInfo.objects.create(
                car_number =item['car_number'],
                firm=item['car_firm'],
                remark=remark
            )

 