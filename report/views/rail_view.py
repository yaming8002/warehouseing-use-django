# Create your views here.
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from report.models import RailReport
from stock.models.site import SiteInfo
from wcommon.utils import MonthListView
from wcommon.utils.uitls import get_year_month


class RailControlView(MonthListView):
    template_name = "rail_report/rail_control.html"

    def get_queryset(self):
        query = ( Q(siteinfo__id__gt=3) )
        return RailReport.get_current_by_query(query)

    def get_whse_martials(self,context ):
        year,month = self.get_year_month()
        # context['kh_stock'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0003'),year,month)
        context['lk_report'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0001'),year,month)
        context['total_report'] = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),year,month)


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

        return render(request,'rail_report/rail_edit.html',context)
    else :
        site_id = request.POST.get('site_id')
        selled =   request.POST.get('selled')
        remark = request.POST.get('remark')
        isdone = request.POST.get('isdone')
        year,month = get_year_month()
        report = RailReport.get_current_by_site(SiteInfo.objects.get(id=site_id))
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
        if report.is_done:
            rail_update__total(report,False)
        context = {'msg':"成功"}
        return JsonResponse(context)


class RailDoneView(MonthListView):
    template_name = "rail_report/rail_done.html"

    def get_queryset(self):
        year,month = self.get_year_month()
        query = (Q(year=year)&Q(month=month)&Q(siteinfo__id__gt=4) )
        return RailReport.get_current_by_query(query,True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        return context
    


def rail_done_withdraw(request):
    if request.method == 'GET':
        site_id = request.GET.get('site_id') 
        report = RailReport.get_current_by_site(SiteInfo.objects.get(id=site_id))
        report.is_done = False
        report.siteinfo.is_rail_done = False
        report.siteinfo.save()
        rail_update__total(report,True)
        report.save()
        context={'msg':"成功退回"}
        return JsonResponse(context)


def rail_update__total(report:RailReport,is_withdraw: bool):
    if report.siteinfo.id < 3:
        return
    
    year,month = get_year_month()
    total = RailReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),year=year,month=month)

    for i in range(5, 17):
        update_value = getattr(report, f'out_{i}') - getattr(report, f'in_{i}')
        update_value *= 1 if is_withdraw else -1
        update_value = Decimal(f'{update_value:.2f}')
        setattr(total, f'in_{i}', getattr(total, f'in_{i}') + update_value)
    total_total =getattr(report, "out_total") - getattr(report, "in_total") 
    total_total = 1 if is_withdraw else -1
    total.in_total += total_total if is_withdraw else -total_total
    total.save() 
