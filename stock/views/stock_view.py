import logging

from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from stock.models.material_model import MatCat, Materials, MatSpec
from stock.models.site_model import SiteInfo
from stock.models.stock_model import Stock
from wcom.utils import PageListView

logger = logging.getLogger(__name__)


class StockView(PageListView):
    model = Stock
    template_name = "stock/stock.html"
    title_name = "庫存"

    def get_queryset(self):
        stock_obj = Stock.objects
        site_obj = SiteInfo.objects.filter(code__in=["0001", "0003"])
        mat_obj = Materials.objects.select_related("category", "specification")
        siteinfo = self.request.GET.get("siteinfo")
        code = self.request.GET.get("code")
        name = self.request.GET.get("name")
        category_id = self.request.GET.get("category_id")
        is_detial = self.request.GET.get("is_detial")
        # 使用 Q 对象构建查询条件

        if is_detial is None:
            mat_obj = mat_obj.filter(specification__in=range(23, 25)).exclude(
                mat_code__in=("2301", "2302")
            )
        query = Q(material__in=mat_obj) & Q(siteinfo__in=site_obj)

        if siteinfo:
            query &= Q(siteinfo_id=siteinfo)
        if code:
            query &= Q(material__mat_code=code)
        if name:
            query &= Q(material__name__istartswith=name)
        if category_id:
            query &= Q(material__category_id=category_id)

        # 更新负数量为0
        stock_obj.filter(query & Q(quantity__lt=0)).update(quantity=0, total_unit=0)

        # 执行查询
        result = stock_obj.filter(query & Q(quantity__gt=0)).order_by(
            "material__mat_code", "material__specification"
        )
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorys"] = MatCat.objects.all()
        context["siteInfos"] = SiteInfo.objects.filter(code__in=["0001", "0003"]).all()
        return context


def getMatrtialData(request):
    if request.method == "GET":
        context = {}
        matrtials = Materials.objects.all().select_related("specification")
        context["matrtials"] = serializers.serialize("json", matrtials)
        context["matcats"] = serializers.serialize("json", MatCat.objects.all())
        context["spec"] = serializers.serialize("json", MatSpec.objects.all())
        context["success"] = True
        return JsonResponse(context)


class ConstnStockViewList(PageListView):
    model = Stock
    template_name = "constn/constn_stock.html"
    title_name = "工地庫存"

    def get_queryset(self):
        owner = self.request.GET.get("owner")
        code = self.request.GET.get("code")
        address = self.request.GET.get("address")
        state = self.request.GET.get("state")
        mat_code = self.request.GET.get("mat_code")
        mat_name = self.request.GET.get("mat_name")
        category_id = self.request.GET.get("category_id")

        query = Q(siteinfo__id__gt=4)
        if code:
            query &= Q(siteinfo__code=code)
        if owner:
            query &= Q(siteinfo__owner__istartswith=owner)
        if address:
            query &= Q(siteinfo__address__istartswith=address)
        if state:
            query &= Q(siteinfo__state=int(state))
        if mat_code:
            query &= Q(material__mat_code=mat_code)
        if mat_name:
            query &= Q(material__mat_name=mat_name)
        if category_id:
            query &= Q(material__category_id=category_id)
        query &= ~(Q(quantity=0) & Q(total_unit=0))
        return Stock.objects.select_related("siteinfo", "material").filter(query).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def split_mat_constn(request):
    if request.method == "GET":
        id = request.GET.get("id")
        constn_stock = Stock.objects.get(id=id)

        context = {"stock": constn_stock}

        return render(request, "constn/split_request.html", context)
    else:
        return render(request, "constn/split_request.html", context)


def stock_edit(request):
    if request.method == "GET":
        report_id = request.GET.get("id")
        report = Stock.objects.get(id=report_id)

        context = {"report": report}

        return render(request, "stock/stock_edit.html", context)
    else:
        report_id = request.POST.get("id")
        quantity = request.POST.get("quantity")
        total_unit = request.POST.get("total_unit", 0)
        Stock.objects.filter(id=report_id).update(
            quantity=quantity, total_unit=total_unit
        )
        context = {"msg": "成功"}
        return JsonResponse(context)
