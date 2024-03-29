
# Create your views here.
from datetime import datetime
from typing import Dict, List

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from decimal import Decimal
from report.models import  SteelReport
from report.models.steel_model import DoneSteelReport, SteelPillar
from stock.models.site import SiteInfo
from wcommon.utils import MonthListView 

from wcommon.utils.uitls import get_year_month

static_column_code = [
        "300",
        "301",
        "350",
        "351",
        "390",
        "400",
        "401",
        "408",
        "414",
        "4141",
        "11",
        "84",
        "88",
        "13",
        "14",
]

class SteelControlView(MonthListView):
    template_name = "steel_report/steel_control.html"

    def get_queryset(self):
        query =  (Q(siteinfo__id__gt=4) )
        return SteelReport.get_current_by_query(query)
            
    def get_whse_martials(self,context ):
        year,month = self.get_year_month()

        context['lk_report'] = SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0001'),year,month)
        context['kh_report'] = SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0003'),year,month)
        context['total_report'] = SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),year,month)
        before_year,before_month = self.get_before_year_month(year,month)
        context['befote_total_report']= SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),before_year,before_month)
        context['diff'] = self.get_diff_value(context['total_report'],context['befote_total_report'])
        context['before_yearMonth'] = f'{before_year}-{before_month:02d}'


    def get_diff_value(self, current, before):
        diff = []
        if current and before:
            current = model_to_dict(current)
            before = model_to_dict(before)
            diff = [(Decimal(current[f'm_{key}']) - Decimal(before[f'm_{key}'])) for key in static_column_code]
        return diff



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)
   
        return context


class SteelDoneView(MonthListView):
    template_name = "steel_report/steel_done.html"

    def get_queryset(self):
        year,month = get_year_month()
        query = (Q(year=year)&Q(month=month)&Q(siteinfo__id__gt=4) & Q(is_done=True) )
        return SteelReport.get_current_by_query(query)
    
    def get_whse_martials(self,context ):
        year,month = get_year_month()
        context['total_report'] = SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),year,month)
        before_year,before_month = self.get_before_year_month()
        context['befote_total_report']= SteelReport.get_current_by_site(SiteInfo.get_site_by_code('0000'),before_year,before_month)
        context['diff'] = self.get_diff_value(context['total_report'],context['befote_total_report'])
        context['before_yearMonth'] = f'{before_year}-{before_month:02d}'

        context['h301'] = SteelPillar.get_value('301',year,month)
        context['h351'] = SteelPillar.get_value('351',year,month)
        context['h401'] = SteelPillar.get_value('401',year,month)

        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)
        return context
    
    def get_diff_value(self,current,before):
        diff = []
        if current and before:
            current = model_to_dict(current)
            before = model_to_dict(before)
            diff = [(current[f'm_{key}'] - before[f'm_{key}']) for key in static_column_code ]
        return diff
    
def get_steel_edit_done(request):
    if request.method == 'GET':
        report_id = request.GET.get('id') 
        report = SteelReport.objects.get(id=report_id)

        context = {'report':report}
        year_month =(datetime.now()).strftime('%Y-%m') 
        split_year_month = [int(x) for x in year_month.split('-')]
        context['year'] = split_year_month[0]
        context['month'] = split_year_month[1]
        context['title'] = '結案編輯'

        
        return render(request,'steel_report/steel_edit.html',context)
    else :
        report_id = request.POST.get('id')
        isdone = request.POST.get('isdone')
        report = SteelReport.objects.select_related('siteinfo').get(id=report_id)
        report.is_done =  isdone is not None and isdone == 'on' 

        if report.is_done :
            # steel_update__total(report,False)
            DoneSteelReport.add_done_item('cut',request)
            DoneSteelReport.add_done_item('change',request)

        context = {'msg':"成功"}
        return JsonResponse(context)
    


def steel_done_withdraw(request):
    if request.method == 'GET':
        report_id = request.GET.get('id') 
        report = SteelReport.objects.select_related('siteinfo').get(id=report_id)
        report.siteinfo.rail_done = False
        report.siteinfo.save()
        steel_update__total(report,True)
        context={'msg':"成功退回"}
        return JsonResponse(context)


def steel_update__total(constn:SteelReport,is_withdraw: bool):
    site = constn.siteinfo
    if site.id < 5:
        return
    
    split_year_month = [int(x) for x in  (datetime.now()).strftime('%Y-%m') .split('-')]
    rail_objects = SteelReport.objects.select_related('siteinfo').filter(Q(year=split_year_month[0])&Q(month=split_year_month[1]))
    total= rail_objects.filter(siteinfo__code='0000').first()

    values= constn.__dict__
    
    for code in static_column_code:
        setattr(total, f'm_{code}', getattr(total, f'm_{code}') + (values.get(f'm_{code}', 0)  if is_withdraw else -values.get(f'm_{code}', 0) ))

    total.save() 