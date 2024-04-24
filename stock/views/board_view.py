# Create your views here.
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from stock.models.board_model import BoardReport
from stock.models.site_model import SiteInfo
from wcommon.utils import MonthListView
from wcommon.utils.uitls import get_year_month


class BoardControlView(MonthListView):
    template_name = "board_report/board_report.html"

    def get_queryset(self):
        mat_code =self.request.GET.get("mat_code")
        mat_code = mat_code if mat_code else '22'
        query = Q(close=False) & Q(siteinfo_id__gte=4) & Q(mat_code = mat_code)
        return BoardReport.objects.filter(query).all() 

    def get_whse_martials(self, context):
        mat_code =self.request.GET.get("mat_code")
        mat_code = mat_code if mat_code else '22'
        obj_board= BoardReport.objects.select_related("siteinfo").filter( Q(mat_code = mat_code))
        context['mat_code'] = mat_code
        context['lk_report'] = obj_board.get(siteinfo__code="0001") if obj_board.filter(siteinfo__code="0001").exists() else None
        context['kh_report'] = obj_board.get(siteinfo__code="0003") if obj_board.filter(siteinfo__code="0003").exists() else None
        # context['lk_report'] = BoardReport.objects.get(siteinfo__code="0001")



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
        context['title'] = '結案編輯'

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