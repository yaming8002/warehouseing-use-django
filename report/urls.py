from django.urls import path
from report.views import steel_pile


urlpatterns = [
    path("steel_pile/", steel_pile, name="steel_pile"),


]
