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
        mat_id =self.request.GET.get("mat_id")
        is_close = self.request.GET.get("is_close" ) != None and self.request.GET.get("is_close" )=='on'
        if mat_id is None:
            return None
        is_lost = "-" in mat_id
        mat_id = '28' if '28' in mat_id  else mat_id
        query =  Q(siteinfo_id__gt=4) & (Q(year__lt=year) | Q(year=year, month__lte=month))
        query &= Q(mat_id=mat_id) & Q(is_lost=is_lost) & ~Q(siteinfo__code = '------')
        final_query = ~( Q(quantity=0) & Q(quantity2=0)) & Q(close=is_close)
        return BoardReport.get_current_by_query(query=query ,final_query=final_query )

    def get_whse_martials(self, context):
        year,month = self.get_year_month()
        mat_id =self.request.GET.get("mat_id")
        context['mat_id'] = mat_id
        if mat_id is None or mat_id=="-28":
            return None
        # obj_board= BoardReport.objects.select_related("siteinfo").filter( Q(mat_code = mat_code))
        context['hui_huang'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('------'),mat_id,year,month)
        context['lk_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0001'),mat_id,year,month)
        if '28' in mat_id :
            context['warning_lk_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0001'),mat_id,year,month,True)
        context['kh_report'] = BoardReport.get_site_matial(SiteInfo.get_site_by_code('0003'),mat_id,year,month)


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
        done_type = request.POST.get('board_stuts')
        is_lost = request.POST.get('is_lost')
        is_close = request.POST.get('is_close')
        member = request.POST.get('member')
        remark = request.POST.get('remark')

        report = BoardReport.objects.select_related('siteinfo').get(id=report_id)
        report.siteinfo.member = member
        report.siteinfo.save()
        report.done_type = done_type
        report.is_lost = is_lost is not None and is_lost == 'on'
        report.close =  is_close is not None and is_close == 'on'
        report.remark = remark if remark else ""
        report.save()


        context = {'msg':"成功"}
        return JsonResponse(context)
