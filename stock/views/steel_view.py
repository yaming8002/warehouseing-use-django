# Create your views here.
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
import copy
from stock.models import SteelReport
from stock.models.done_steel_model import DoneSteelReport
from stock.models.site_model import SiteInfo
from trans.service.update_done_steel_by_month import update_total_by_month
from wcom.utils import MonthListView
from wcom.utils.uitls import get_year_month


class SteelControlView(MonthListView):
    template_name = "steel_report/steel_control.html"

    def get_queryset(self):
        year, month = self.get_year_month()
        query = Q(siteinfo__id__gt=4) & (
            Q(year__lt=year) | Q(year=year, month__lte=month)
        )
        exclude_query = Q()
        for x in SteelReport.static_column_code.keys():
            exclude_query |= ~Q(**{f"m_{x}": 0})
        return SteelReport.get_current_by_query(query, final_query=exclude_query)

    def get_whse_martials(self, context):
        year, month = self.get_year_month()

        context["lk_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0001"), year, month
        )
        context["kh_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0003"), year, month
        )
        context["total_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0000"), year, month
        )
        before_year, before_month = self.get_before_year_month(year, month)
        context["befote_total_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0000"), before_year, before_month
        )
        context["diff"] = self.get_diff_value(
            context["total_report"], context["befote_total_report"]
        )
        context["before_yearMonth"] = f"{before_year}-{before_month:02d}"

    def get_diff_value(self, current: SteelReport, before: SteelReport):
        diff = []
        if current and before:
            currentdata = model_to_dict(current)
            beforedata = model_to_dict(before)
            diff = [
                (float(currentdata[f"m_{key}"]) - float(beforedata[f"m_{key}"]))
                for key in SteelReport.static_column_code.keys()
            ]
        return diff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)

        return context


class SteelDoneView(MonthListView):
    template_name = "steel_report/steel_done.html"

    def get_queryset(self):
        year, month = self.get_year_month()
        query = Q(year=year) & Q(month=month) & Q(is_done=True)
        return DoneSteelReport.objects.filter(query).all()

    def get_whse_martials(self, context):
        year, month = self.get_year_month()
        sum_report = self.get_queryset()
        context["total_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0000"), year, month
        )
        before_year, before_month = self.get_before_year_month(year, month)
        context["befote_total_report"] = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code("0000"), before_year, before_month
        )
        context["sum_report"] = copy.deepcopy(context["befote_total_report"])
        for code in SteelReport.static_column_code:
            column = f"m_{code}"
            for item in sum_report:
                setattr(
                    context["sum_report"],
                    column,
                    getattr(context["sum_report"], column) + getattr(item, column),
                )

        context["diff"] = self.get_diff_value(
            context["total_report"], context["sum_report"]
        )
        context["before_yearMonth"] = f"{before_year}-{before_month:02d}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)
        return context

    def get_diff_value(self, current, before):
        diff = []
        if current and before:
            current = model_to_dict(current)
            before = model_to_dict(before)
            diff = [
                (current[f"m_{key}"] - before[f"m_{key}"])
                for key in SteelReport.static_column_code.keys()
            ]
        return diff


def get_steel_edit_done(request):
    if request.method == "GET":
        report_id = request.GET.get("id")
        report = SteelReport.objects.get(id=report_id)

        context = {"report": report}
        year_month = (datetime.now()).strftime("%Y-%m")
        split_year_month = [int(x) for x in year_month.split("-")]
        context["year"] = split_year_month[0]
        context["month"] = split_year_month[1]
        context["title"] = "結案編輯"
        context["yearMonth"] = f"{report.year}-{report.month:02d}"

        return render(request, "steel_report/steel_edit.html", context)
    else:
        report_id = request.POST.get("id")
        site_code = request.POST.get("siteinfo_code")
        isdone = request.POST.get("isdone")
        y, m = get_year_month(request.POST.get("yearMonth"))
        # report = SteelReport.objects.select_related('siteinfo').get(id=report_id)
        report = SteelReport.get_current_by_site(
            SiteInfo.get_site_by_code(site_code), y, m
        )
        report.is_done = isdone is not None and isdone == "on"
        report.save()
        if report.is_done:
            DoneSteelReport.add_done_item("cut", request)
            DoneSteelReport.add_done_item("change", request)
            query = Q(siteinfo=SiteInfo.get_site_by_code(site_code)) & (
                Q(year=y, month__gt=m) | Q(year__gt=y)
            )
            SteelReport.objects.filter(query).delete()
        update_total_by_month(y, m)
        context = {"msg": "成功"}
        return JsonResponse(context)


def steel_done_withdraw(request):
    if request.method == "GET":
        report_id = request.GET.get("id")
        # print(report_id)
        report = DoneSteelReport.objects.select_related("siteinfo").get(id=report_id)
        report.is_done = False
        report.save()
        query = (
            Q(year__lt=report.year) | Q(year=report.year, month__lte=report.month)
        ) & Q(siteinfo=report.siteinfo)
        steel = SteelReport.get_current_by_query(query).first()
        steel.is_done = False
        steel.save()
        context = {"msg": "成功退回"}
        return JsonResponse(context)


def get_edit_remark(request):
    if request.method == "GET":
        report_id = request.GET.get("id")
        report = DoneSteelReport.objects.get(id=report_id)
        context = {"report": report}

        return render(request, "steel_report/steel_edit_remark.html", context)
    else:
        report_id = request.POST.get("id")
        report = DoneSteelReport.objects.get(id=report_id)
        report.remark = request.POST.get("remark")
        diff_dct = defaultdict(lambda: Decimal(0))
        for mat_code in DoneSteelReport.static_column_code.keys():
            column = f"m_{mat_code}"
            value_str = request.POST.get(column)
            value = Decimal(value_str) if value_str else Decimal(0)
            diff_dct[column] = getattr(report, column) - value
            setattr(report, column, value)

        report.save()
        update_total_by_month(report.year, report.month)
        from_report = SteelReport.get_current_by_site(
            report.siteinfo, report.year, report.month
        )
        trun_reprot = SteelReport.get_current_by_site(
            report.turn_site if report.turn_site else SiteInfo.get_warehouse(),
            report.year,
            report.month,
        )
        print(diff_dct)
        for k, v in diff_dct.items():
            setattr(from_report, k, getattr(from_report, k) + v)
            setattr(trun_reprot, k, getattr(trun_reprot, k) - v)
        from_report.save()
        trun_reprot.save()

        context = {"msg": "成功"}
        return JsonResponse(context)
