from django.shortcuts import render

from report.util.steel_brace import build_steel_brace_table
from report.util.steel_pile import  build_steel_ng_table, build_steel_pile_table
from stock.models.site import SiteInfo

# Create your views here.


def steel_brace_view(request):
    # 将查询结果传递给模板
    context = {}
    if request.method == "GET":
        owner = request.GET.get("owner")
        code = request.GET.get("code")
        name = request.GET.get("name")
        constn = SiteInfo.objects.filter(genre=1)
        show = False
        if owner:
            constn = constn.filter(owner=owner)
            show = True
        if code:
            constn = constn.filter(code=code)
            show = True
        if name:
            constn = constn.filter(name=name)
            show = True

        if show and constn.exists():
            context["steel_pile_table"] = build_steel_brace_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(14)

    return render(request, "constn_report/steel_brace.html", context)



def steel_pile_view(request):
    # 将查询结果传递给模板
    context = {}
    if request.method == "GET":
        owner = request.GET.get("owner")
        code = request.GET.get("code")
        name = request.GET.get("name")
        constn = SiteInfo.objects.filter(genre=1)
        show = False
        if owner:
            constn = constn.filter(owner=owner)
            show = True
        if code:
            constn = constn.filter(code=code)
            show = True
        if name:
            constn = constn.filter(name=name)
            show = True
        

        steel_ng_map = {"300": "H300", "350": "H350", "400": "H400","3050": "鋼軌"}
        if show and constn.exists():
            context["steel_pile_table"] = build_steel_pile_table(constn.get())
            context["steel_ng_table"] = build_steel_ng_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(2)

    return render(request, "constn_report/steel_pile.html", context)