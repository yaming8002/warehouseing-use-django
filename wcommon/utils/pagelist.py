from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.views.generic.list import ListView
from datetime import datetime, timedelta

class PageListView(ListView):
    paginate_by = 20
    context_object_name = 'pagelist'
    forms = forms.Form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context["pagelist"], self.paginate_by)
        page = self.request.GET.get('page')
        try:
            pagelist = paginator.page(page)
        except PageNotAnInteger:
            pagelist = paginator.page(1)
        except EmptyPage:
            pagelist = paginator.page(paginator.num_pages)
        context["begin"] ,context["end"] = self.get_month_range()
        context['pagelist'] = pagelist
        context['from'] = forms
        return context

    def get_month_range(self):
        # 获取当前日期
        if self.request.GET.get("begin"):
            # 将字符串转换为 datetime 对象
            self.begin = datetime.strptime(self.request.GET.get("begin"), "%Y-%m-%d")
            self.end = datetime.strptime(self.request.GET.get("end"), "%Y-%m-%d")
        else:
            today = datetime.today()
            # 获取这个月的第一天
            self.begin = today.replace(day=1)
            # 获取下个月的第一天，然后减去一天得到这个月的最后一天
            self.end = (self.begin.replace(month=self.begin.month % 12 + 1, day=1) - timedelta(days=1))

        return self.begin, self.end