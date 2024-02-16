from datetime import date
import datetime
from decimal import Decimal
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from constn.models import ConStock, Construction
from trans.models import CarInfo, TransportDetailLog, TransportLog
from wcommon.utils.pagelist import PageListView
from whse.models.material import MatCat, MatList, MatSpec
from whse.models.whse import Stock, StockBase, WhseList


class CarListView(PageListView):
    model = CarInfo
    template_name = "trans/carinfo.html"

    def get_queryset(self):
        result = CarInfo.objects
        car_number = self.request.GET.get("car_number")
        firm = self.request.GET.get("firm")
        patload = self.request.GET.get("patload")

        if car_number:
            result = result.filter(car_number__istartswith=car_number)
        if firm:
            result = result.filter(firm__startswith=firm)
        if patload:
            result = result.filter(patload=patload)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "車輛清單"
        return context


def transport_log_from(request, log_type):
    if request.method == "GET":
        context = {}
        context["constructions"] = Construction.objects.all()
        context["whses"] = WhseList.objects.all()
        context["cars"] = CarInfo.objects.all()
        context["title"] = "出料單" if "out" in request.path else "入料單"
        context["action"] = (
            "transport_log/output" if log_type == "output" else "transport_log/input"
        )
        context["code"] = datetime.today() 
        return render(request, "trans/transport_log.html", context)
    else:
        constn = Construction.objects.get(code=request.POST.get("construction"))
        tran = TransportLog.objects.create(
            code=request.POST.get("code"),
            construction=constn,
            whse=WhseList.objects.get(id=request.POST.get("whse")),
            level=request.POST.get("level"),
            car=CarInfo.objects.get(car_number=request.POST.get("car_number")),
            transaction_type="IN" if "in" in log_type else "OUT",
            member=request.POST.get("member"),
        )

        index = 0
        while request.POST.get(f"mat_item[{index}].id"):
            mat_id = int(request.POST.get(f"mat_item[{index}].id"))
            quantity = Decimal(request.POST.get(f"mat_item[{index}].quantity"))
            unit_req = request.POST.get(f"mat_item[{index}].unit")
            unit = Decimal(unit_req) if unit_req != '---' else Decimal(0)
            print(quantity)
            mat = MatList.objects.get(id=mat_id)
            TransportDetailLog.objects.create(
                logistics=tran,
                material=mat,
                quantity=quantity,
                all_quantity=quantity,
                unit=unit,
                all_unit=unit * quantity if unit  else unit,
            )
           
            stock = Stock.objects.get(materiel=mat)
            chang_quantity_util( "in" in log_type ,stock, quantity ,unit )
            print(mat.id)
            print(constn.code)
            con_stock_fifter = ConStock.objects.filter(construction=constn, materiel=mat)
            print(f'con_stock_fifter.count(){con_stock_fifter.count()}')
            if con_stock_fifter.count() > 0 :
                con_stock = con_stock_fifter.get()
                chang_quantity_util( "out" in log_type ,con_stock, quantity ,unit )
                con_stock.save()
            else:
                print("data not find")
                new_con_stock = ConStock.objects.create(
                    construction=constn,
                    materiel=mat,
                )
                chang_quantity_util( True ,new_con_stock, quantity ,unit )
                new_con_stock.save()
        context = {"success": True, "msg": "成功"}

        return JsonResponse(context)

def chang_quantity_util(isadd:bool,whse:StockBase, quantity:Decimal ,unit:Decimal ):
    """
    Args:
        isadd (bool): _description_
        whse (Stock): _description_
        quantity (_type_): _description_
        unit (_type_): _description_
        用於調控數量與次級單位的計算
    """
    if isadd:
        whse.quantity += quantity
        if unit:
            whse.unit += unit * quantity
    else:
        whse.quantity -= quantity
        if unit:
            whse.unit -= unit * quantity



def getMatrtialData(request):
    if request.method == "GET":
        context = {}
        matrtials = MatList.objects.all().select_related("specification")
        context["matrtials"] = serializers.serialize("json", matrtials)
        context["matcats"] = serializers.serialize("json", MatCat.objects.all())
        context["spec"] = serializers.serialize("json", MatSpec.objects.all())
        context["success"] = True
        return JsonResponse(context)
