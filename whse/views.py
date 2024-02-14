import logging
from django.views.generic.list import ListView
from wcommon.utils.excel_tool import ImportDataGeneric
from whse.froms.material import MatListForm
from django.views.generic.edit import CreateView, UpdateView
from whse.models.material import MatCat, MatList, MatSpec
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from whse.models.whse import Stock, WhseList

logger = logging.getLogger(__name__)


# Create your views here.
class MatListView(ListView):
    model = MatList
    template_name = "whse/matlist.html"
    context_object_name = "matList"
    paginate_by = 20  # 每頁顯示的項目數量

    def get_queryset(self):
        result = MatList.objects
        code = self.request.GET.get("mat_code")
        name = self.request.GET.get("name")
        category_id = self.request.GET.get("category_id")

        if name:
            result = result.filter(name__istartswith=name)
        if code:
            result = result.filter(mat_code=code)
        if category_id:
            category = MatCat.objects.get(id=category_id)
            result = result.filter(category=category)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "物料清單"
        # 将查询条件传递到模板
        context["mat_code"] = self.request.GET.get("mat_code", "")
        context["name"] = self.request.GET.get("name", "")
        context["category"] = self.request.GET.get("category_id", "")
        context["category_list"] = MatCat.objects.all()
        paginator = Paginator(context["matList"], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            matList = paginator.page(page)
        except PageNotAnInteger:
            matList = paginator.page(1)
        except EmptyPage:
            matList = paginator.page(paginator.num_pages)
        context['matList'] = matList
        return context


class ImportMaterialView(ImportDataGeneric):
    title = "上傳EXCEL"
    action = "/material/uploadexcel/"
    columns = ["料號", "料名", "類型", "規格", "耗材", "拆分", "拆分單位"]

    def insertDB(self, actual_columns):
        matcatset = MatCat.objects
        matspceset = MatSpec.objects 
        for item in actual_columns :
            print(item)
            if(item[0] is None):
                break

            code = (
                str(item[0])
                if isinstance(item[0], (int, str))
                else "{:.0f}".format(item[0])
            )
            mat = MatList(mat_code=code,name=str(item[1]))
            mat.category = matcatset.filter(name=item[2]).first()
            mat.specification = matspceset.filter(name=item[3]).first()
            mat.is_consumable = item[4]=="YES"
            mat.is_divisible = item[5] == "YES"
            mat.unit_of_division = item[6]
            mat.save()

class MaterialCreateView(CreateView):  # noqa: F821
    model = MatList
    form_class = MatListForm
    template_name = "base/model_edit.html"

    def form_valid(self, form):
        """如果表單數據有效，則執行此方法。"""
        form.save()
        return JsonResponse({"status": "success", "msg": "新增成功"})

    def form_invalid(self, form):
        """如果表單數據無效，則執行此方法。"""
        logger.error("表單數據無效：%s", form.errors)
        return JsonResponse({"status": "error", "msg": form.errors.as_json()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 将查询条件传递到模板
        context["action"] = "/material/add/"
        context["title"] = "新增物料"
        context["is_add"] = True
        return context
    

class MaterialUpdataView(UpdateView):  # noqa: F821
    model = MatList
    form_class = MatListForm
    template_name = "base/model_edit.html"

    def get_initial(self):
        # 獲取要編輯的物料對象
        material = self.get_object()

        # 返回初始數據
        return model_to_dict(material)

    def form_valid(self, form):
        """如果表單數據有效，則執行此方法。"""
        form.save()
        return JsonResponse({"status": "success", "msg": "新增成功"})

    def form_invalid(self, form):
        """如果表單數據無效，則執行此方法。"""
        logger.error("表單數據無效：%s", form.errors)
        return JsonResponse({"status": "error", "msg": form.errors.as_json()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 将查询条件传递到模板
        context["action"] = "/material/updata/"
        context["title"] = "編輯物料"
        context["is_add"] = False
        return context

class WhseListView(ListView):
    model = Stock 
    template_name = "whse/whse.html"
    context_object_name = "stock"
    paginate_by = 20
    
    def get_queryset(self):
        stock_obj = Stock.objects.select_related('whse')
        mat_obj = MatList.objects.select_related('category', 'specification').filter(~Q(specification=23))
        whse_id = self.request.GET.get("whse_id")
        mat_code = self.request.GET.get("mat_code")
        category_id = self.request.GET.get("category_id")
        if whse_id:
            stock_obj = stock_obj.filter(whse=whse_id)
        if mat_code:
            mat_obj = mat_obj.filter(mat_code=mat_code)
        if category_id:
            mat_obj = mat_obj.filter(category=category_id)

        # mat_pref = Prefetch('materiel', queryset=mat_obj)  # left join
        # result = stock_obj.prefetch_related(mat_pref)
        result = stock_obj.filter(materiel__in=mat_obj) # inner join
        return result
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "庫存"
        # 将查询条件传递到模板
        context["category_list"] = MatCat.objects.all()
        context["whse_list"] = WhseList.objects.all()

        paginator = Paginator(context["stock"], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            stockList = paginator.page(page)
        except PageNotAnInteger:
            stockList = paginator.page(1)
        except EmptyPage:
            stockList = paginator.page(paginator.num_pages)
        context['stock'] = stockList
        return context