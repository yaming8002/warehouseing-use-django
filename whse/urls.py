from django.urls import path

from whse.views import ImportMaterialView, MatListView, MaterialCreateView, MaterialUpdataView, WhseListView

urlpatterns = [
    path("material/list/", MatListView.as_view(), name="material"),
    path(
        "material/uploadexcel/",
        ImportMaterialView.as_view(),
        name="material_uploadexcel",
    ),
    path("material/add/", MaterialCreateView.as_view(), name="material"),
    path("material/edit/", MaterialUpdataView.as_view(), name="material"),
    
    path("whse/list/", WhseListView.as_view(), name="group"),
    # path("whse/add/", group_add, name="group"),
    # path("whse/edit/", group_edit, name="group"),
    
    # path("material/add/", MuserCreateView.as_view(), name="account"),
    # path("material/edit/", account_edit, name="account"),
    # path("material/upload/", account_edit, name="account"),
    # path("whse/list/", GroupListView.as_view(), name="group"),
    # path("whse/add/", group_add, name="group"),
    # path("whse/edit/", group_edit, name="group"),
    # path("stock/list/", GroupListView.as_view(), name="group"),
    # path("stock/Modify/", group_add, name="group"),
]
