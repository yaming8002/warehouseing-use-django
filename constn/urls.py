from django.urls import path

from constn.views import ConstnStockViewList, ConstnViewList

urlpatterns = [
    path("constn/list/", ConstnViewList.as_view(), name="constn"),
    path("constn_stock/list/", ConstnStockViewList.as_view(), name="constn"),
]
