import logging

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from constn.froms import ConstnForm

from constn.models import ConStock, Construction
from wcommon.utils.excel_tool import ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from wcommon.templatetags import constn_state
from django.shortcuts import get_object_or_404
from django.utils import timezone

from wcommon.utils.save_control import SaveControlView

# Create your views here.
logger = logging.getLogger(__name__)


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

        stock = ConStock.objects.select_related("materiel")
        result = stock.filter(construction__in=constn.all())
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "工地庫存"
        return context


class ImportConstnView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/constn/uploadexcel/"
    columns = [
        "工地編號",
        "業主",
        "工程名稱",
        "地點",
        "發案日期",
        "狀態",
        "現場人員",
        "計價人員",
        "結案日期",
        "備註",
    ]

    def insertDB(self, actual_columns):
        for item in actual_columns:
            if item[0] is None:
                break
            crate_date = datetime.now()

            if item[4]:
                crate_date = datetime.strptime(item[4], '%Y-%m-%d')
            code = (
                str(item[0])
                if isinstance(item[0], (int, str))
                else "{:.0f}".format(item[0]).zfill(4)
            )
            state = 1
            state_name = str(item[5])
            for x in constn_state:
                if state_name == x[1]:
                    state = x[0]
                    break
            try:
                Construction.objects.create(
                    code=code,
                    owner=str(item[1]),
                    name=str(item[2]),
                    address=str(item[3]),
                    crate_date=crate_date,
                    state=state,
                )
            except Exception as e:
                # 处理可能的异常情况
                print("An error occurred:", e)
                self.response_data["error_list"].append((code,str(e)))

    
class ConstnSeveView(SaveControlView): 
    name = '工廠資訊'
    model= Construction
    form_class = ConstnForm

    def form_is_valid(self ,form):
        if form.cleaned_data.get('state') == 0:
            form.instance.done_date = timezone.now().date()
        else :
            form.instance.done_date =None




def split_mat_constn(request):
    if request.method == "GET":
        id = request.GET.get('id')
        constn_stock = ConStock.objects.get(id=id)

        context = {"stock":constn_stock}
        
        return render(request, "constn/split_request.html", context)
    else:
        return render(request, "constn/split_request.html", context)
    