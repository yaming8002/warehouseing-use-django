from django.shortcuts import render

from constn.models import ConStock, Construction
from wcommon.utils.pagelist import PageListView

# Create your views here.
class ConstnViewList(PageListView):
    model = Construction
    template_name = "constn/constn.html"

    def get_queryset(self):
        result = Construction.objects
        owner = self.request.GET.get("owner")
        code = self.request.GET.get("code")
        address = self.request.GET.get("address")
        state = self.request.GET.get("state")
      
        if code:
            result = result.filter(code=code)
        if owner:
            result = result.filter(owner__istartswith=owner)
        if address:
            result = result.filter(address__istartswith=address)
        if state:
            state_int = int(state)
            result = result.filter(state=state_int)
        
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "車輛清單"
        return context
    

class ConstnStockViewList(PageListView):
    model = ConStock
    template_name = "constn/constn_stock.html"

    def get_queryset(self):
        constn = Construction.objects
        owner = self.request.GET.get("owner")
        code = self.request.GET.get("code")
        address = self.request.GET.get("address")
        state = self.request.GET.get("state")
      
        if code:
            constn = constn.filter(code=code)
        if owner:
            constn = constn.filter(owner__istartswith=owner)
        if address:
            constn = constn.filter(address__istartswith=address)
        if state:
            state_int = int(state)
            constn = constn.filter(state=state_int)

        stock = ConStock.objects.select_related('materiel')
        result = stock.filter(construction__in=constn.all()) 
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "工地庫存"
        return context