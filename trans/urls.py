from django.urls import path
from trans.views import CarListView

urlpatterns = [
    path("carinfo/list/", CarListView.as_view(), name="carinfo"),


]
