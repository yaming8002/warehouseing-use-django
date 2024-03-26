from django.urls import path
from trans.views import CarInfoControlView, CarListView, ImportCarInfoView, ImportTransportView, TrandportView, TransRentView
from trans.views.transportlog_view import TransTurn

urlpatterns = [
    path("carinfo/list/", CarListView.as_view(), name="carinfo"),
    path("carinfo/save/", CarInfoControlView.as_view(), name="carinfo"),
    path("carinfo/uploadexcel/", ImportCarInfoView.as_view(), name="carinfo"),
    path("transport_log/uploadexcel/", ImportTransportView.as_view(), name="carinfo"),

    # path("transport_request/<str:log_type>/", transport_log_from, name="carinfo"),
    path("transport_log/list/", TrandportView.as_view(), name="transport_log"),
    # path("transport_log/uploadexcel/", ImportTransportView.as_view(), name="carinfo"),

    # path("inputform/", CarListView.as_view(), name="carinfo"),
    path("tran_rent/list/", TransRentView.as_view(), name="carinfo"),
    path("tran_turn/list/", TransTurn.as_view(), name="tran_turn"),

]
