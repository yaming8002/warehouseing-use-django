from django.urls import path

from stock.views.materials import ImportMaterialView, MaterialSeveView, MaterialsView, getMatrtialData
from stock.views.site import ConstnSeveView, ImportConstnView, SiteViewList
from stock.views.stock import ConstnStockViewList, StockView

urlpatterns = [
    path("material/list/", MaterialsView.as_view(), name="material"),
    path(
        "material/uploadexcel/",
        ImportMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path("material/save/", MaterialSeveView.as_view(), name="material_sabe"),
    path("getMatrtialData/", getMatrtialData, name="carinfo"),
    
    path("stock/list/", StockView.as_view(), name="stock"),
    path("constn_stock/list/", ConstnStockViewList.as_view(), name="constn"),
    
    path("constn/list/", SiteViewList.as_view(), name="constn"),
    path('constn/edit/', ConstnSeveView.as_view(), name='construction_update'),
    path("constn/uploadexcel/", ImportConstnView.as_view(), name="constn"),
    
    # path("split/material/", split_mat_constn, name="split_mat"),


]
