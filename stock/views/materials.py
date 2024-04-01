import logging

from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView 
from django.views import View
from wcommon.utils.excel_tool import ImportData2Generic, ImportDataGeneric
from wcommon.utils.pagelist import PageListView
from stock.froms.material import MaterialsForm
from stock.models.material import MatCat, Materials, MatSpec
from wcommon.utils.save_control import SaveControlView

logger = logging.getLogger(__name__)


# Create your views here.
class MaterialsView(PageListView):
    model = Materials
    template_name = "stock/materials.html"
    title_name = "物料清單"

    def get_queryset(self):
        result = Materials.objects
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
        # 将查询条件传递到模板
        context["mat_code"] = self.request.GET.get("mat_code", "")
        context["name"] = self.request.GET.get("name", "")
        context["category"] = self.request.GET.get("category_id", "")
        context["category_list"] = MatCat.objects.all()
        print(context["category_list"])
        return context


class ImportMaterialView(ImportData2Generic):
    title = "上傳EXCEL"
    action = "/material/uploadexcel/"
    columns = [
        "料號",
        "入料號",
        "出料號",
        "料名",
        "類型",
        "規格",
        "耗材",
        "拆分",
        "拆分單位",
        "備註",
    ]

    def insertDB(self, item):
        matcatset = MatCat.objects
        matspceset = MatSpec.objects
        if item[0] is None:
            return 

        code = (
            str(item[0])
            if isinstance(item[0], (int, str))
            else "{:.0f}".format(item[0])
        )
    
        if item[1] is None:
            code1 = None
        else :
            code1= (
                    str(item[1])
                    if isinstance(item[1], (int, str))
                    else "{:.0f}".format(item[1])
            )
            
        if item[2] is None:
            code2 = None
        else :
            code2= (
                    str(item[2])
                    if isinstance(item[2], (int, str))
                    else "{:.0f}".format(item[2])
                )

        # mat = Materials(mat_code=code,name=str(item[1]))
        print(f"code{code},mat_code2:{code1},mat_code3:{code2},name={item[3]}")
        Materials.objects.create(
            mat_code=code,
            mat_code2=code1,
            mat_code3=code2,
            name=str(item[3]),
            category=matcatset.filter(name=item[4]).first(),
            specification=None if item[5] == "無" else matspceset.filter(name=item[5]).first(),
            is_consumable=item[6] == "是",
            is_divisible=item[7] == "是",
            unit_of_division=item[8],
        )




# class MaterialCreateView(CreateView):  # noqa: F821
#     model = Materials
#     form_class = MaterialsForm
#     template_name = "base/model_edit.html"

#     def form_valid(self, form):
#         """如果表單數據有效，則執行此方法。"""
#         form.save()
#         return JsonResponse({"status": "success", "msg": "新增成功"})

#     def form_invalid(self, form):
#         """如果表單數據無效，則執行此方法。"""
#         logger.error("表單數據無效：%s", form.errors)
#         return JsonResponse({"status": "error", "msg": form.errors.as_json()})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # 将查询条件传递到模板
#         context["action"] = "/material/add/"
#         context["title"] = "新增物料"
#         context["is_add"] = True
#         return context


# class MaterialUpdataView(UpdateView):  # noqa: F821
#     model = Materials
#     form_class = MaterialsForm
#     template_name = "base/model_edit.html"

#     def get_initial(self):
#         # 獲取要編輯的物料對象
#         material = self.get_object()

#         # 返回初始數據
#         return model_to_dict(material)

#     def form_valid(self, form):
#         """如果表單數據有效，則執行此方法。"""
#         form.save()
#         return JsonResponse({"status": "success", "msg": "新增成功"})

#     def form_invalid(self, form):
#         """如果表單數據無效，則執行此方法。"""
#         logger.error("表單數據無效：%s", form.errors)
#         return JsonResponse({"status": "error", "msg": form.errors.as_json()})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # 将查询条件传递到模板
#         context["action"] = "/material/updata/"
#         context["title"] = "編輯物料"
#         context["is_add"] = False
#         return context


class MaterialSeveView(SaveControlView):
    name = "物料"
    model = Materials
    form_class = MaterialsForm


def getMatrtialData(request):
    if request.method == "GET":
        context = {}
        context["matrtials"] = serializers.serialize("json", Materials.objects.all())
        context["matcats"] = serializers.serialize("json", MatCat.objects.all())
        context["spec"] = serializers.serialize("json", MatSpec.objects.all())
        context["success"] = True
        return JsonResponse(context)
