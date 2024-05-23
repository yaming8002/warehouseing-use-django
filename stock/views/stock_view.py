import logging
from datetime import datetime, timedelta

from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from stock.froms.material import MaterialsForm
from stock.models.material_model import MatCat, Materials, MatSpec
from stock.models.site_model import SiteInfo
from stock.models.stock_model import  Stock
from wcom.templatetags import constn_state
from wcom.utils import ImportDataGeneric
from wcom.utils import PageListView
from wcom.utils.save_control import SaveControlView

logger = logging.getLogger(__name__)

class StockView(PageListView):
    model = Stock 
    template_name = "stock/stock.html"
    title_name = "庫存"
    
    def get_queryset(self):
        stock_obj = Stock.objects
        site_obj = SiteInfo.objects.filter(genre=0)
        mat_obj = Materials.objects.select_related('category', 'specification').filter(~Q(specification=23))
        siteinfo = self.request.GET.get("siteinfo")
        code = self.request.GET.get("code")
        name = self.request.GET.get("name")
        category_id = self.request.GET.get("category_id")
        
        if siteinfo:
            site_obj = site_obj.filter(id=siteinfo)
        if code:
            mat_obj = mat_obj.filter(mat_code=code)
        if name:
            mat_obj = mat_obj.filter(name__istartswith=name)
        if category_id:
            mat_obj = mat_obj.filter(category=category_id)
        stock_obj.filter(material__in=mat_obj,siteinfo__in=site_obj,quantity__lt=0).update(quantity=0)
        result = stock_obj.filter(material__in=mat_obj,siteinfo__in=site_obj,quantity__gt=0) # inner join
        return result.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorys"] = MatCat.objects.all()
        context["siteInfos"] = SiteInfo.objects.filter(genre=0).all()
        return context
    
def getMatrtialData(request):
    if request.method == "GET":
        context = {}
        matrtials = Materials.objects.all().select_related("specification")
        context["matrtials"] = serializers.serialize("json", matrtials)
        context["matcats"] = serializers.serialize("json", MatCat.objects.all())
        context["spec"] = serializers.serialize("json", MatSpec.objects.all())
        context["success"] = True
        return JsonResponse(context)
    
class ConstnStockViewList(PageListView):
    model = Stock
    template_name = "constn/constn_stock.html"
    title_name = "工地庫存"

    def get_queryset(self):
        constn = SiteInfo.objects.filter()
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

        stock = Stock.objects.select_related("material")
        result = stock.filter(siteinfo__in=constn.all())
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
def split_mat_constn(request):
    if request.method == "GET":
        id = request.GET.get('id')
        constn_stock = Stock.objects.get(id=id)

        context = {"stock":constn_stock}
        
        return render(request, "constn/split_request.html", context)
    else:
        return render(request, "constn/split_request.html", context)