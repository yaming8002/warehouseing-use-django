from django.urls import path
from trans.views import CarInfoControlView, CarListView, ImportCarInfoView, ImportTransportView, TrandportView, transport_log_from

urlpatterns = [
    path("carinfo/list/", CarListView.as_view(), name="carinfo"),
    path("carinfo/save/", CarInfoControlView.as_view(), name="carinfo"),
    path("carinfo/uploadexcel/", ImportCarInfoView.as_view(), name="carinfo"),


    path("transport_request/<str:log_type>/", transport_log_from, name="carinfo"),
    path("transport_log/list/", TrandportView.as_view(), name="carinfo"),
    path("transport_log/uploadexcel/", ImportTransportView.as_view(), name="carinfo"),
    # path("inputform/", CarListView.as_view(), name="carinfo"),

]
