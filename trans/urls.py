from django.urls import path
from trans.views import CarListView, TrandportView, getMatrtialData, transport_log_from

urlpatterns = [
    path("carinfo/list/", CarListView.as_view(), name="carinfo"),
    path("transport_request/<str:log_type>/", transport_log_from, name="carinfo"),
    path("getMatrtialData/", getMatrtialData, name="carinfo"),
    path("transport_log/list/", TrandportView.as_view(), name="carinfo"),
    # path("inputform/", CarListView.as_view(), name="carinfo"),

]
