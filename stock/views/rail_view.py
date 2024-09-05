# Create your views here.
from decimal import Decimal

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from stock.models import RailReport
from stock.models.site_model import SiteInfo
from trans.service.update_rail_by_month import count_done_report
from wcom.utils import MonthListView
from wcom.utils.uitls import get_year_month


class RailControlView(MonthListView):
    template_name = "rail_report/rail_control.html"

    def get_queryset(self):
        year,month = self.get_year_month()
        query =  Q(siteinfo__id__gt=3) & (Q(year__lt=year) | Q(year=year, month__lte=month))
        final_query = ~(Q(in_total = 0) & Q(out_total=0))
        return RailReport.get_current_by_query(query,final_query)

    def get_whse_martials(self,context ):
        year,month = self.get_year_month()
        # context['kh_stock'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0003'),year,month)
        context['lk_report'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0001'),year,month)
        context['total_report'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),year,month)
        lst = self.object_list
        summary = {}
        for i in range(5, 17):
            in_field_sum = sum(getattr(item, f"in_{i}", 0) for item in lst)
            out_field_sum = sum(getattr(item, f"out_{i}", 0) for item in lst)
            summary[f"in_{i}"] = in_field_sum
            summary[f"out_{i}"] = out_field_sum
        summary["in_total"] = sum(getattr(item, "in_total", 0) for item in lst)
        summary["out_total"] = sum(getattr(item, "out_total", 0) for item in lst)
        summary["rail_ng"] = sum(getattr(item, "rail_ng", 0) for item in lst)
        context["summary"] = summary


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)
        return context



def get_rail_edit_done(request):
    if request.method == 'GET':
        report_id = request.GET.get('id')
        report = RailReport.objects.get(id=report_id)
        values= report.__dict__
        sum={}
        for i in range(5,17):
            sum[f'sum_{i}'] = values[f'in_{i}']-values[f'out_{i}']
        sum['sum_total'] = values['in_total']-values['out_total']

        context = {'report':report,'sum':sum}
        context['title'] = '結案編輯'
        context['yearMonth'] = f'{report.year}-{report.month:02d}'

        return render(request,'rail_report/rail_edit.html',context)
    else :
        site_id = request.POST.get('site_id')
        selled = request.POST.get('selled')
        remark = request.POST.get('remark')
        isdone = request.POST.get('isdone')
        year,month = get_year_month(request.POST.get('yearMonth'))
        report = RailReport.get_current_by_site(SiteInfo.objects.get(id=site_id), year,month)
        report.done_type = 1 if selled is not None and selled == 'on' else 0

        report.remark = remark
        report.is_done =  isdone is not None and isdone == 'on'
        report.siteinfo.is_rail_done = report.is_done
        report.siteinfo.save()
        if f'{report.year}{report.month}' < f'{year}{month}' :
            report.pk = None
            report.year = year
            report.month = month

        report.save()

        q = Q(siteinfo=report.siteinfo) & ((Q(year=report.year, month__gt=report.month) | Q(year__gt=report.year)))
        RailReport.objects.filter(q).delete()

        count_done_report( year, month)
        context = {'msg':"成功"}
        return JsonResponse(context)


class RailDoneView(MonthListView):
    template_name = "rail_report/rail_done.html"

    def get_queryset(self):
        year,month = self.get_year_month()
        query = (Q(year=year)&Q(month=month)&Q(siteinfo__id__gt=4) )
        return RailReport.get_current_by_query(query=query,is_done=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context



def rail_done_withdraw(request):
    if request.method == 'GET':
        # site_id = request.GET.get('site_id')
        id = request.GET.get('id')
        report = RailReport.objects.get(id=id)
        report.is_done = False
        report.siteinfo.is_rail_done = False
        report.siteinfo.save()
        report.save()
        count_done_report( report.year,report.month )
        context={'msg':"成功退回"}
        return JsonResponse(context)


def rail_update__total(report:RailReport,is_withdraw: bool , year,month):
    if report.siteinfo.id < 3:
        return

    total_list = RailReport.objects.filter(siteinfo =SiteInfo.get_site_by_code('0000'),year__gte=year,month__gte=month).all()
    for total in total_list :
        for i in range(5, 17):
            update_value =   getattr(report, f'out_{i}') - getattr(report, f'in_{i}')
            update_value = Decimal(f'{update_value:.2f}')
            update_value = update_value if is_withdraw  else -1*update_value
            setattr(total, f'in_{i}', getattr(total, f'in_{i}') + update_value)
        report_total =  report.out_total -report.in_total
        report_total = report_total if is_withdraw  else -1*report_total
        total.in_total += report_total
        total.save()
