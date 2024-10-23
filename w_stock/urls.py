from django.urls import path


from w_stock.views.materials_view import DownloadMaterialView, ImportMaterialView, MaterialSeveView, MaterialsView
from w_stock.views.site_view import ConstnSeveView, ImportConstnView, ImportSiteInfoByTotalView, SiteViewList, get_sitelist
from w_stock.views.stock_view import ConstnStockViewList, StockView, stock_edit

urlpatterns = [
    path("material/list/", MaterialsView.as_view(), name="material"),
    path(
        "material/uploadexcel/",
        ImportMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path(
        "material/download/",
        DownloadMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path("material/save/", MaterialSeveView.as_view(), name="material_sabe"),
    # path("getMatrtialData/", getMatrtialData, name="carinfo"),
    path("stock/list/", StockView.as_view(), name="stock"),
    path("stock/edit/", stock_edit, name="stock"),
    path("constn_stock/list/", ConstnStockViewList.as_view(), name="constn"),
    path("constn/list/", SiteViewList.as_view(), name="constn"),
    path("constn/get_sitelist/", get_sitelist, name="constn"),
    path("constn/edit/", ConstnSeveView.as_view(), name="construction_update"),
    path("constn/uploadexcel/", ImportConstnView.as_view(), name="constn"),
    path(
        "constn/uploadexcelByTotal/",
        ImportSiteInfoByTotalView.as_view(),
        name="material_uploadexcel",
    ),

]
