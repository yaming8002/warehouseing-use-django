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
from constn.models import ConStock, Construction
from trans.models import CarInfo, TransportDetailLog, TransportLog
from wcommon.utils.excel_tool import ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from whse.models.material import MatCat, Materials, MatSpec
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


class TrandportView(PageListView):
    model = TransportDetailLog
    template_name = "trans/trandport_log.html"

    def get_queryset(self):
        
        detail = TransportDetailLog.objects
        log = TransportLog.objects
        material = Materials.objects
        car = CarInfo.objects
        construction = Construction.objects

        begin, end = self.get_month_range()
        print([begin, end])
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
            log = log.filter(whse=whse)
        if code:
            log = log.filter(code__istartswith=code)
        if member:
            log = log.filter(member__startswith=member)
        if tran_type:
            log = log.filter(transaction_type=tran_type)

        if constn:
            construction = construction.filter(id=constn)

        # 过滤 Materials
        if matinfo_core:
            material = material.filter(mat_code=matinfo_core)
        if matinfo_cat:
            material = material.filter(category= MatCat.objects.get(name=matinfo_cat))
        if matinfo_name:
            material = material.filter(name__istartswith=matinfo_name)

        # 过滤 CarInfo
        if car_com:
            car = car.filter(firm__istartswith=car_com)
        if car_number:
            car = car.filter(car_number__istartswith=car_number)

        # 使用过滤后的 log 过滤 detail
        log = log.filter(construction__in=construction.all(), car__in=car.all())
        detail = detail.filter(material__in=material.all(), logistics__in=log.all())

        return detail.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "出入總表"
        context["whses"] = WhseList.objects.all()
        context["matinfo_cats"] = MatCat.objects.all()

        return context


def transport_log_from(request, log_type):
    if request.method == "GET":
        context = {}
        context["constructions"] = Construction.objects.all()
        context["whses"] = WhseList.objects.all()
        context["cars"] = CarInfo.objects.all()
        context["title"] = "出料單" if "out" in request.path else "入料單"
        context["action"] = (
            "transport_request/output"
            if log_type == "output"
            else "transport_request/input"
        )

        return render(request, "trans/transport_request.html", context)
    else:
        constn = Construction.objects.get(id=request.POST.get("construction"))
        print(request.POST.get("whse")) 
        whse=WhseList.objects.get(id=request.POST.get("whse"))
        tran = TransportLog.objects.create(
            code=request.POST.get("code"),
            construction=constn,
            whse=whse,
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
            unit = Decimal(unit_req) if unit_req != "---" else Decimal(0)

            mat = Materials.objects.get(id=mat_id)
            TransportDetailLog.objects.create(
                logistics=tran,
                material=mat,
                quantity=quantity,
                all_quantity=quantity,
                unit=unit,
                all_unit=unit * quantity if unit else unit,
            )

            # stock = Stock.objects.get(whse=whse, materiel=mat)
            # chang_quantity_util("in" in log_type, stock, quantity, unit)
            # print(mat.id)
            # print(constn.code)
            # con_stock_fifter = ConStock.objects.filter(
            #     construction=constn, materiel=mat
            # )
            # stock.save()
            # print(f"con_stock_fifter.count(){con_stock_fifter.count()}")
            # if con_stock_fifter.count() > 0:
            #     con_stock = con_stock_fifter.get()
            #     chang_quantity_util("out" in log_type, con_stock, quantity, unit)
            #     con_stock.save()
            # else:
            #     print("data not find")
            #     new_con_stock = ConStock.objects.create(
            #         construction=constn,
            #         materiel=mat,
            #     )
            #     chang_quantity_util(True, new_con_stock, quantity, unit)
            #     new_con_stock.save()
            index += 1
        context = {"success": True, "msg": "成功"}

        return JsonResponse(context)



class ImportTransportView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/transport_log/uploadexcel/"
    columns = [
        "日期",
        "出入料",
        "工地編號",
        "單據編號",
        "物料編號",
        "實際米數",
        "出(入)庫量",
        "出(入)米數",
        "施工層別",
        "車號" ,
        "人員",
    ]

    def insertDB(self, actual_columns):
        whse = WhseList.objects.get(id=1)
        constn = Construction.objects
        carlist = CarInfo.objects
        Trans_all = TransportLog.objects
        for item in actual_columns:
            if item[0] is None:
                break
            trancode = str(item[3])

            constn_code = (
                str(item[2])
                if isinstance(item[2], (int, str))
                else "{:.0f}".format(item[2])
            )
            car_id=(
                str(item[9])
                if isinstance(item[9], (int, str))
                else "{:.0f}".format(item[9])
            )
            
            build_date = datetime.strptime(str(item[0]), '%Y-%m-%d %H:%M:%S')
        
            try:
                tran = Trans_all.filter(code=trancode).first()
                if not tran :  
                    tran = Trans_all.create(
                        code = trancode,
                        whse = whse,
                        construction = constn.get(code=constn_code),
                        build_date = build_date,
                        car = carlist.get(car_number=car_id),
                        transaction_type ='IN' if "入" in str( item[1]) else 'OUT',
                        level = item[8] if item[8] else 0,
                        member= item[10]
                    )
                self.build_detial(tran ,item,("入" in item[1]),whse, constn.get(code=constn_code) )

            except Exception as e:
                # 处理可能的异常情况
                print("insertDB An error occurred:", e)
                self.response_data["error_list"].append((trancode,str(e)))


    def build_detial(self ,tran:TransportLog, item:[],log_type: bool,whse:WhseList,constn:Construction) :
        try:
            unit_req = item[5]
            unit = Decimal(unit_req) if unit_req else Decimal(0)
            quantity = Decimal(item[6]) 
            mat_code = (
                    str(item[4])
                    if isinstance(item[4], (int, str))
                    else "{:.0f}".format(item[4])
                )
            mat_object = Materials.objects
            if  unit_req:
                spec = MatSpec.objects.get(id = round(unit))
                mat = mat_object.get(mat_code=mat_code,specification=spec)
            else :
                mat = mat_object.get(mat_code=mat_code)
            print( f"'{mat.name}'")
            
            TransportDetailLog.objects.create(
                    logistics = tran,
                    material = mat,
                    quantity =quantity,
                    all_quantity = quantity,
                    unit = unit,
                    all_unit = unit* quantity if unit else unit,
                    remark = item,
            )
        except Exception as e:
            # 处理可能的异常情况
            print("build_detial An error occurred:", item,e)


        
