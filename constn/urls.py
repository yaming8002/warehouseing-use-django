from django.urls import path

from constn.views import ConstnSeveView, ConstnStockViewList, ConstnViewList, ImportConstnView,  split_mat_constn

urlpatterns = [
    path("constn/list/", ConstnViewList.as_view(), name="constn"),
    # path('constn/edit/<int:construction_id>/', constn_control_view, name='construction_update'),
    path('constn/edit/', ConstnSeveView.as_view(), name='construction_update'),
    path("constn/uploadexcel/", ImportConstnView.as_view(), name="constn"),
    path("constn_stock/list/", ConstnStockViewList.as_view(), name="constn"),
    path("material/split/constn/", split_mat_constn, name="split_mat"),
]
