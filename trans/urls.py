from django.urls import path
from trans.views import CarInfoControlView, CarListView, ImportCarInfoView, ImportTransportView, TrandportView, TransRentView
from trans.views.carinfo_view import ImportCarInfoByTotalView
from trans.views.transportlog_view import TransTurn, trans_detial_rollback_view, update_end_date

urlpatterns = [
    # carinfo
    path("carinfo/list/", CarListView.as_view(), name="carinfo"),
    path("carinfo/save/", CarInfoControlView.as_view(), name="carinfo"),
    path("carinfo/uploadexcel/", ImportCarInfoView.as_view(), name="carinfo"),
    path("carinfo/uploadexcelByTotal/", ImportCarInfoByTotalView.as_view(), name="carinfo"),
    # total table upload
    path("transport_log/uploadexcel/", ImportTransportView.as_view(), name="carinfo"),
    path("update_end_date/",update_end_date,name="update_end_date"),
    # transport_log
    path("transport_log/list/", TrandportView.as_view(), name="transport_log"),
    # path("transport_log/edit/", TransDetialControlView.as_view(), name="transport_log"),
    path("transport_log/remove/", trans_detial_rollback_view, name="transport_log"),

    # other table
    path("tran_rent/list/", TransRentView.as_view(), name="carinfo"),
    path("tran_turn/list/", TransTurn.as_view(), name="tran_turn"),

]
