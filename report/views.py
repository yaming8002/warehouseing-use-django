import decimal
import math
from django.shortcuts import render
from report.util.steel_pile import build_steel_pile_table
from stock.models.material import Materials
from decimal import Decimal
from typing import List, Dict
from stock.models.site import SiteInfo
from trans.models import TransportDetailLog, TransportLog

# Create your views here.


def steel_pile(request):
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
            context["steel_pile_table"] = build_steel_pile_table(constn)
            context["constn"] = constn.get()
            context["column_count"] = range(14)

    return render(request, "conreports/steel_pile.html", context)
