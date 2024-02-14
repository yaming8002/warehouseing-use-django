from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.views.generic.list import ListView

from trans.models import CarInfo
from wcommon.utils.pagelist import PageListView

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