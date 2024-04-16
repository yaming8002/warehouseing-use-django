import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from openpyxl import load_workbook

from stock.models.steel_model import DoneSteelReport
from stock.models.material_model import MatCat, Materials, MatSpec
from stock.models.site_model import SiteInfo
from trans.forms import CarinfoFrom
from trans.models import CarInfo, TransLog, TransLogDetail
from wcommon.utils.excel_tool import ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from wcommon.utils.save_control import SaveControlView
from wcommon.utils.uitls import excel_value_to_str, get_month_range

class TransRentView(PageListView):
    model = TransLogDetail
    template_name = "trans/trans_rent.html"
    title_name = "租賃表"

    def get_queryset(self):
        detail = TransLogDetail.objects
        log = TransLog.objects
        material = Materials.objects
        car = CarInfo.objects
        construction = SiteInfo.objects

        begin, end = self.get_month_range()
        whse = self.request.GET.get("whse")
        code = self.request.GET.get("code")
        constn = self.request.GET.get("constn")
        matinfo_core = self.request.GET.get("matinfo_core")
        matinfo_name = self.request.GET.get("matinfo_name")
        matinfo_cat = self.request.GET.get("matinfo_cat")
        car_com = self.request.GET.get("car_com")
        car_number = self.request.GET.get("car_number")
        member = self.request.GET.get("member")
        tran_type = self.request.GET.get("tran_type")

        # 过滤 TransportLog
        if begin and end:
            log = log.filter(build_date__range=[begin, end])
        if whse:
            log = log.filter(form_site=construction.get(id=whse))
        if code:
            log = log.filter(code__istartswith=code)
        if member:
            log = log.filter(member__startswith=member)
        if tran_type:
            log = log.filter(transaction_type=tran_type)

        if constn:
            construction = construction.get(id=constn)

        # 过滤 Materials
        if matinfo_core:
            material = material.filter(mat_code=matinfo_core)
        if matinfo_cat:
            material = material.filter(category=MatCat.objects.get(name=matinfo_cat))
        if matinfo_name:
            material = material.filter(name__istartswith=matinfo_name)

        # 过滤 CarInfo
        if car_com:
            car = car.filter(firm__istartswith=car_com)
        if car_number:
            car = car.filter(car_number__istartswith=car_number)

        # 使用过滤后的 log 过滤 detail
        log = log.filter(constn_site__in=construction.all(), carinfo__in=car.all())
        detail = detail.filter(is_rent=True,material__in=material.all(), translog__in=log.all())

        return detail.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "出入總表"
        context["whses"] = SiteInfo.objects.filter(genre=0).all()
        context["matinfo_cats"] = MatCat.objects.all()

        return context