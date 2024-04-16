from django.shortcuts import render

from stock.util.steel_brace import build_steel_brace_table
from stock.util.steel_pile import  build_steel_ng_table, build_steel_pile_table
from stock.models.site_model import SiteInfo
from wcommon.templatetags.strmap import get_level

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

        level = request.GET.get("level")
        level = int(level) if level else 7
    
        if show and constn.exists():
            context["steel_pile_table"] = build_steel_brace_table(constn.get(),level)
            context["constn"] = constn.get()
            context["select_level"]= [x for x in get_level() if (x[0]>0)]
            context["table_level"]= level
            context["column_count"] = range(level*2)

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
        
  

        if show and constn.exists():
            # context["steel_pile_table"] = build_steel_pile_table(constn.get())
            context["steel_ng_table"] = build_steel_ng_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(2)

    return render(request, "constn_report/steel_pile.html", context)

def component_view(request):
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
        

        # steel_ng_map = {"10": "補強板", "6300": "H300止水板","6350": "H350止水板","6400": "H400止水板",
        #                  "79": "擋土板","9": "防墬網/安全網","11":"覆工板","12":"洗車板","21": "鋪路鐵板 全", "2105":"鋪路鐵板 半" ,
        #                   "13": "千斤頂","14": "土壓計",
        #                   "11":"樓梯","12":"小鐵板0.8*1.5","21": "小鐵板1*2", "2105":"斜撐",
        #                    "13": "安全步道 1M","14": "伸縮梯","11":"伸縮臂","12":"牛頭","21": "小鐵板1*2", "2105":"斜撐" }
        if show and constn.exists():
            context["steel_pile_table"] = build_steel_pile_table(constn.get())
            context["steel_ng_table"] = build_steel_ng_table(constn.get())
            context["constn"] = constn.get()
            context["column_count"] = range(2)

    return render(request, "constn_report/steel_pile.html", context)
