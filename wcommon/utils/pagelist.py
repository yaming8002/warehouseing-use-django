from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from django.http import Http404
from django.views.generic.list import ListView

class PageListView(ListView):
    paginate_by = 20
    context_object_name = 'pagelist'

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
        context['pagelist'] = pagelist
        return context