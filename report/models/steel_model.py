from datetime import datetime
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F, Q
from django.utils.timezone import datetime

from report.models.monthreport_model import MonthData, MonthReport
from stock.models.material import Materials
from stock.models.site import SiteInfo
from stock.models.stock import MainStock
from trans.models import TransLog, TransLogDetail
from wcommon.templatetags import done_type_map
from wcommon.utils.uitls import excel_value_to_str, get_year_month
from decimal import Decimal ,ROUND_HALF_UP
from django.forms.models import model_to_dict
import logging
# # Create your models here.
import logging.config
from django.conf import settings

logging.config.dictConfig(settings.LOGGING)

logger = logging.getLogger(__name__)

class SteelReport(MonthReport):
    static_column_code = {
        "300": "H300*300",
        "301": "H300中柱",
        "350": "H350*350",
        "351": "H350中柱",
        "390": "H390*400",
        "400": "H400*400",
        "401": "H400中柱",
        "408": "H408*400",
        "414": "H414*405",
        "4141": "H414中柱",
        "11": "覆工板 1M *2M",
        "84": "覆工板 1M *3M",
        "88": "水泥覆工板",
        "13": "千斤頂",
        "14": "土壓計",
    }

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0, verbose_name=v
        )

    @classmethod
    def add_report(
        cls,
        translog: TransLog,
        is_in: bool,
        mat: Materials,
        all_quantity: Decimal,
        all_unit: Decimal,
    ):
        if mat.mat_code not in cls.static_column_code.keys():
            return 
        
        site= translog.constn_site
        year,month = translog.build_date.year ,translog.build_date.month
        report = cls.get_current_by_site(site,year,month)
        whse = cls.get_current_by_site(SiteInfo.objects.get(code='0001'),year,month)
        value =all_unit if mat.is_divisible else all_quantity

        float_value = getattr(report, f'm_{mat.mat_code}')
        if isinstance(float_value, float):
            float_value = Decimal(str(float_value))

        if is_in:
            setattr(report,f'm_{mat.mat_code}',report.get_column_decimal_val(f'm_{mat.mat_code}')-value )
            setattr(whse,f'm_{mat.mat_code}',whse.get_column_decimal_val(f'm_{mat.mat_code}')+value )
        else:
            setattr(report,f'm_{mat.mat_code}',report.get_column_decimal_val(f'm_{mat.mat_code}')+value )
            setattr(whse,f'm_{mat.mat_code}',whse.get_column_decimal_val(f'm_{mat.mat_code}')-value )
        # logger.info(model_to_dict(report))
        whse.save()
        report.save() 
    


class DoneSteelReport(MonthReport):
    static_column_code = {
        "300": "H300*300",
        "301": "H300中柱",
        "350": "H350*350",
        "351": "H350中柱",
        "390": "H390*400",
        "400": "H400*400",
        "401": "H400中柱",
        "408": "H408*400",
        "414": "H414*405",
        "4141": "H414中柱",
        "11": "覆工板 1M *2M",
        "84": "覆工板 1M *3M",
        "88": "水泥覆工板",
        "13": "千斤頂",
        "14": "土壓計",
    }

    for k, v in static_column_code.items():
        locals()[f"m_{k}"] = models.DecimalField(
            max_digits=10, decimal_places=2, default=0.0 ,null=True, verbose_name=v
        )

    class Meta:
        verbose_name = "變動資訊"
        verbose_name_plural = "變動資訊"
        ordering = ["done_type", "id"]  # 按照 id 升序排序

    @classmethod
    def add_stock(cls,tran:TransLog, item):
        mat_code = excel_value_to_str(item[7])
        unit_req = item[9]
        quantity = Decimal(abs(item[15]))
        unit = Decimal(unit_req).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if unit_req else None
        mat_code = excel_value_to_str(item[7])
        remark = excel_value_to_str(item[20])
        mat = Materials.get_item_by_code(mat_code,remark, unit)
        if mat.mat_code not in cls.static_column_code.keys() :
            return 
        
        y,m = get_year_month()
        site = tran.constn_site
        done_report_obj = cls.objects.select_related("siteinfo").filter(
            siteinfo=site,
            done_type = 2,
        )

        if done_report_obj.exists() :
            done_report = done_report_obj.first()
        else:
            done_report = cls.objects.create(
                siteinfo=site,
                done_type = 2,
                year=y,
                month=m,
                is_done=True,
                remark = excel_value_to_str(item[20]) 
            )

        setattr(done_report,f'm_{mat.mat_code}', unit * quantity if unit else quantity )
        
        done_report.save()


    @classmethod
    def add_done_item(cls, case_name, request):
        # print(f"{case_name}")
        site_id = request.POST.get("siteinfo_id")
        type_val = request.POST.get(f"{case_name}.done_type")
        isdone = request.POST.get('isdone')  is not None and  request.POST.get('isdone') == 'on' 
        site = SiteInfo.objects.get(id=site_id)
        y,m = get_year_month()
        done_report_obj = cls.objects.select_related("siteinfo").filter(
            siteinfo=site,
            done_type = type_val,
        )

        if done_report_obj.exists() :
            done_report = done_report_obj.first()
        else:
            done_report = cls.objects.create(
                siteinfo=site,
                done_type = type_val,
                year=y,
                month=m,
                is_done=isdone,
                remark = request.POST.get(f"{case_name}.remark")
            )

        for k, _ in done_report.static_column_code.items() :
            # print(f"{case_name}.m_{k}")
            # print(request.POST.get(f"{case_name}.m_{k}"))
            setattr(done_report,f'm_{k}', request.POST.get(f"{case_name}.m_{k}"))
        
        done_report.save()

        

            



class SteelItem(MonthReport):
    steel = models.ForeignKey(
        SteelReport,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        verbose_name="地點",
    )

    year = models.IntegerField(default=2010, verbose_name="年")
    month = models.IntegerField(default=1, verbose_name="月份")

    material = models.ForeignKey(
        Materials, on_delete=models.CASCADE, verbose_name="物料"
    )

    all_quantity = models.IntegerField(default=0, verbose_name="總數量")

    class Meta:
        unique_together = ["steel", "material", "all_quantity"]
        ordering = ["id"]  # 按照 id 升序排序


class SteelPillar(MonthData):
    edit_date = models.DateTimeField(default=datetime.now)
    mat_code = models.CharField(max_length=10, default="", verbose_name="物料代號")
    for i in range(1, 18):
        locals()[f"l_{i}"] = models.IntegerField(default=0, verbose_name=f"In_{i}")
    total = models.IntegerField(default=0, verbose_name="總計")

    @classmethod
    def get_value(cls, mat_code, year, month):
        query = Q(mat_code=mat_code) & Q(year=year) & Q(month=month)
        sp, _ = cls.objects.get_or_create(mat_code=mat_code, year=year, month=month)
        return sp

    @classmethod
    def update_value(cls, mat_code, year, month):
        if mat_code not in ("301", "351", "401"):
            return
        query = Q(mat_code=mat_code) & Q(year=year) & Q(month=month)
        sp, _ = cls.objects.get_or_create(**query)
        stock_objs = MainStock.objects.select_related("material").filter(
            id=2, material__mat_code=mat_code
        )
        for i in range(1, 18):  # Start from 1, since you start from 1 in field names
            stock = stock_objs.get(material__specification=i)
            setattr(sp, f"l_{i}", stock.quantity)
        sp.save()

    class Meta:
        unique_together = ["year", "month", "mat_code"]
