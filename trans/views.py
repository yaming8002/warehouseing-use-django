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
from trans.models import CarInfo, TransportDetailLog, TransportLog
from wcommon.utils.excel_tool import ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from stock.models.material import MatCat, Materials, MatSpec
from wcommon.utils.save_control import SaveControlView
from wcommon.utils.uitls import excel_value_to_str


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


class CarInfoControlView(SaveControlView):
    name = "車輛資訊"
    model = CarInfo
    form_class = CarinfoFrom


class ImportCarInfoView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/carinfo/uploadexcel/"
    columns = ["車牌號碼", "駕駛員", "吊卡車公司", "噸數", "基本台金", "備註"]

    def insertDB(self, actual_columns):
        for item in actual_columns:
            if item[0] is None:
                break
            code = excel_value_to_str(item[0])
            
            try:
                if CarInfo.objects.filter(car_number=code).exists():
                    print(f"{code} is exists")
                else :
                    CarInfo.objects.create(
                        car_number=code,
                        driver=item[1],
                        firm= item[2] if item[2] else '',
                        patload=item[3],
                        value=Decimal(item[4]) if item[4] else Decimal(0),
                        remark=item[5],
                    )   
            except Exception as e:
                # 处理可能的异常情况
                print(f"{item} insertDB An error occurred:{e}")
                self.error_list.append((item, e))


class TrandportView(PageListView):
    model = TransportDetailLog
    template_name = "trans/trandport_log.html"

    def get_queryset(self):
        detail = TransportDetailLog.objects
        log = TransportLog.objects
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
        log = log.filter(to_site__in=construction.all(), car__in=car.all())
        detail = detail.filter(material__in=material.all(), transportlog__in=log.all())

        return detail.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "出入總表"
        context["whses"] = SiteInfo.objects.filter(genre=0).all()
        context["matinfo_cats"] = MatCat.objects.all()

        return context


def transport_log_from(request, log_type):
    if request.method == "GET":
        context = {}
        context["constructions"] = SiteInfo.objects.filter(genre=1).all()
        context["whses"] = SiteInfo.objects.filter(genre=0).all()
        context["cars"] = CarInfo.objects.all()
        context["title"] = "出料單" if "out" in request.path else "入料單"
        context["action"] = (
            "transport_request/output"
            if log_type == "output"
            else "transport_request/input"
        )

        return render(request, "trans/transport_request.html", context)
    else:
        constn = SiteInfo.objects.get(id=request.POST.get("construction"))

        whse = SiteInfo.objects.get(id=request.POST.get("whse"))
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
                transportlog=tran,
                material=mat,
                quantity=quantity,
                all_quantity=quantity,
                unit=unit,
                all_unit=unit * quantity if unit else unit,
            )

            index += 1
        context = {"success": True, "msg": "成功"}

        return JsonResponse(context)

import sys 

class ImportTransportView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/transport_log/uploadexcel/"
    columns = [
        "日期",
        "來源工地編號",
        "目的工地編號",
        "轉單",
        "單據編號",
        "物料編號",
        "實際米數",
        "出(入)庫量",
        "出(入)米數",
        "施工層別",
        "車號",
        "人員",
        "備註",
    ]

    def insertDB(self, actual_columns):

        main_site_obj = SiteInfo.objects.filter(genre=0)
        consite_obj = SiteInfo.objects.filter(genre=1)
        turn_site_obj = SiteInfo.objects
        carlist = CarInfo.objects
        Trans_all = TransportLog.objects
        for item in actual_columns:
            # print(item)
            if item[0] is None and item[4] is None:
                break 
            if item[1] is None and item[2] is None:
                continue
            from_site = excel_value_to_str(item[1])
            to_site = excel_value_to_str(item[2])
            turn_site = excel_value_to_str(item[3])
   
            if (
                main_site_obj.filter(code=from_site).exists()
                and main_site_obj.filter(code=to_site).exists()
            ):
                transaction_type = "OUT"
                form_site = main_site_obj.get(code=from_site)
                to_site = main_site_obj.get(code=from_site)
                turn_site = None
            elif (
                main_site_obj.filter(code=from_site).exists()
                and consite_obj.filter(code=to_site).exists()
            ):
                transaction_type = "OUT"
                form_site = main_site_obj.get(code=from_site)
                to_site = consite_obj.get(code=to_site)
                turn_site = turn_site_obj.get(code=turn_site) if turn_site else None 
            else:
                transaction_type = "IN"
                form_site = main_site_obj.get(code=to_site)
                to_site = consite_obj.get(code=from_site)
                turn_site = turn_site_obj.get(code=turn_site) if turn_site else None 

            trancode = excel_value_to_str(item[4])
            car_id = excel_value_to_str(item[10])
            if carlist.filter(car_number=car_id).exists():
                carinfo = carlist.get(car_number=car_id) 
            elif  car_id :
                carinfo = carlist.create(
                    car_number=car_id,
                    remark=f"{item}"
                )
            else : 
                carinfo = None 
            try:
                # transaction_type 轉單必須進單與出單分別列出
                tran = Trans_all.filter(code=trancode,transaction_type=transaction_type).first()
                if not tran:
                    tran = Trans_all.create(
                        code=trancode,
                        form_site=form_site,
                        to_site=to_site,
                        turn_site = turn_site,
                        build_date=item[0],
                        car=carinfo,
                        transaction_type=transaction_type,
                        member=item[11],
                    )

                self.build_detial(
                    tran,
                    item,
                )

            except Exception as e:
                # 处理可能的异常情况
                print(item)
                print("insertDB An error occurred:", e)
                self.error_list.append((item, e))
                sys.exit()

    def build_detial(self, tran: TransportLog, item: list):
        if item[5] is None :
            self.error_list.append(f"{item}: 沒有物料資訊")
            print(f"{item}: 沒有物料資訊")
            return 
        try:
            unit_req = item[6]
            unit = Decimal(unit_req) if unit_req else Decimal(0)
            quantity = Decimal(item[7])
            mat_code = excel_value_to_str(item[5])
            mat_object = Materials.objects
            if unit_req:
                spec = MatSpec.objects.get(id=round(unit))
                mat = mat_object.get(
                    ( Q(mat_code=mat_code) | Q(mat_code2=mat_code) | Q(mat_code3=mat_code))
                    & Q(specification=spec)
                )
            else:
                mat = mat_object.get(
                    Q(mat_code=mat_code) | Q(mat_code2=mat_code) | Q(mat_code3=mat_code)
                )
            
            TransportDetailLog.objects.create(
                transportlog=tran,
                material=mat,
                level=item[9] if item[9] else None,
                quantity=quantity,
                all_quantity=quantity,
                unit=unit,
                all_unit=unit * quantity if unit else unit,
                remark=item[12],
            )
        except Exception as e:
            # 处理可能的异常情况
            print("build_detial An error occurred:", item, e)
            self.error_list.append((item, e))
            sys.exit()
