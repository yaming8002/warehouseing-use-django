from django.shortcuts import render

from constn.models import Construction
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