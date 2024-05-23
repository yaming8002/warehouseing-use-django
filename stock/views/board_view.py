# Create your views here.
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from stock.models.board_model import BoardReport
from stock.models.site_model import SiteInfo
from wcom.utils import MonthListView
from wcom.utils.uitls import get_year_month


class BoardControlView(MonthListView):
    template_name = "board_report/board_report.html"

    def get_queryset(self):
        year,month = self.get_year_month()
        mat_code =self.request.GET.get("mat_code")
        if mat_code is None:
            return None
        is_lost = "-" in mat_code
        mat_code = '22' if '22' in mat_code  else mat_code
        query = Q(close=False) & Q(siteinfo_id__gt=4) & (Q(year__lt=year) | Q(year=year, month__lte=month))
        query &= Q(mat_code=mat_code) & Q(is_lost=is_lost)
        query &= ~(Q(quantity=0) & Q(quantity2=0))

        return BoardReport.get_current_by_query(query)

    def get_whse_martials(self, context):
        year,month = self.get_year_month()
        mat_code =self.request.GET.get("mat_code")
        context['mat_code'] = mat_code
        if mat_code is None or mat_code=="-22":
            return None
        # obj_board= BoardReport.objects.select_related("siteinfo").filter( Q(mat_code = mat_code))
        
        context['lk_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0001'),mat_code,year,month)
        if '22' in mat_code :
            context['warning_lk_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0001'),mat_code,year,month,True)
        context['kh_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0003'),mat_code,year,month)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_whse_martials(context)

        return context

def get_board_edit_done(request):
    if request.method == 'GET':
        report_id = request.GET.get('id') 
        report = BoardReport.objects.get(id=report_id)

        context = {'report':report}
        year_month =(datetime.now()).strftime('%Y-%m') 
        split_year_month = [int(x) for x in year_month.split('-')]
        context['year'] = split_year_month[0]
        context['month'] = split_year_month[1]
        context['title'] = '編輯'

        return render(request,'board_report/board_edit.html',context)
    else :
        report_id = request.POST.get('id')
        is_done = request.POST.get('is_done')
        done_type = request.POST.get('done_type')
        close = request.POST.get('close')
        is_lost = request.POST.get('is_lost')
        member = request.POST.get('member')
        remark = request.POST.get('remark')

        report = BoardReport.objects.select_related('siteinfo').get(id=report_id)
        report.siteinfo.member = member
        report.siteinfo.save()
        report.is_done =  is_done is not None and is_done == 'on' 
        report.done_type = 1 if done_type is not None and done_type == 'on'  else 0
        report.close = close is not None and close == 'on' 
        report.is_lost = is_lost is not None and is_lost == 'on' 
        report.remark = remark if remark else ""
        report.save()


        context = {'msg':"成功"}
        return JsonResponse(context)