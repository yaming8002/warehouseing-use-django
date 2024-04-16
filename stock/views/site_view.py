import logging

from django.core import serializers
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from stock.froms.site import SiteInfoForm
from stock.models.stock_model import MainStock
from datetime import datetime, timezone
from wcommon.utils.excel_tool import ImportData2Generic, ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from stock.froms.material import MaterialsForm
from stock.models.material_model import MatCat, Materials, MatSpec
from stock.models.site_model import SiteInfo
from wcommon.utils.save_control import SaveControlView
from wcommon.templatetags import constn_state, site_genre
from wcommon.utils.uitls import excel_value_to_str, tup_map_get_index


logger = logging.getLogger(__name__)


class SiteViewList(PageListView):
    model = SiteInfo
    template_name = "constn/constn.html"
    title_name = "工地列表"

    def get_queryset(self):
        result = SiteInfo.objects
        owner = self.request.GET.get("owner")
        code = self.request.GET.get("code")
        name = self.request.GET.get("name")
        state = self.request.GET.get("state")
        genre = self.request.GET.get("genre")

        if code:
            result = result.filter(code=code)
        if owner:
            result = result.filter(owner__istartswith=owner)
        if name:
            result = result.filter(name__istartswith=name)
        if state:
            state_int = int(state)
            result = result.filter(state=state_int)
        if genre:
            genre_int = int(genre)
            result = result.filter(genre=genre_int)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ImportConstnView(ImportData2Generic):
    title = "上傳EXCEL"
    action = "/constn/uploadexcel/"
    min_row = 2
    columns = [
        "工地編號",
        "業主",
        "工程名稱",
        "發案日期",
        "分類",
        "狀態",
        "現場人員",
        "計價人員",
        "結案日期",
        "備註",
    ]

    def insertDB(self, item):
  
        if item[0] is None:
            return 
        crate_date = datetime.now()
        done_date = datetime.now()
        if item[3]:
            crate_date = datetime.strptime(item[3], "%Y-%m-%d")
        if item[8]:
            done_date = datetime.strptime(item[8], "%Y-%m-%d")
        
        code = excel_value_to_str(item[0])
        genre = tup_map_get_index(site_genre, item[4])  # noqa: F821
        state = tup_map_get_index(constn_state, item[5])
        done_date = None if state >0 else done_date

        try:
            if SiteInfo.objects.filter(code=code).exists():
                print(f"{code} is exists ")    
            else:
                SiteInfo.objects.create(
                    code=code,
                    owner=str(item[1]),
                    name=item[2],
                    crate_date=crate_date,
                    genre=genre,
                    state=state,
                    member=item[6],
                    counter=item[7],
                    done_date=done_date,
                    remark=item[9],
                )
        except Exception as e:
            # 处理可能的异常情况
            print("An error occurred:", e)
            self.response_data["error_list"].append((code, str(e)))


class ConstnSeveView(SaveControlView):
    name = "工地資訊"
    model = SiteInfo
    form_class = SiteInfoForm

    def form_is_valid(self, form):
        if form.cleaned_data.get("state") == 0:
            form.instance.done_date = timezone.now().date()
        else:
            form.instance.done_date = None
