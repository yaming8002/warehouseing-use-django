from django.urls import path

from constn.views import ConstnViewList

urlpatterns = [
    path("constn/list/", ConstnViewList.as_view(), name="constn"),
]
