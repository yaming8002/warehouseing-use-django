from django.urls import path

from whse.views import ImportMaterialView, MaterialsView, MaterialCreateView, MaterialUpdataView, StockView,  getMatrtialData

urlpatterns = [
    path("material/list/", MaterialsView.as_view(), name="material"),
    path(
        "material/uploadexcel/",
        ImportMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path("material/add/", MaterialCreateView.as_view(), name="material"),
    path("material/edit/", MaterialUpdataView.as_view(), name="material"),
    
    path("stock/list/", StockView.as_view(), name="stock"),

    path("getMatrtialData/", getMatrtialData, name="carinfo"),

]
