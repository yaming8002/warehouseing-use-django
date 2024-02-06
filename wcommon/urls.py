from wcommon.views import (
    AccountLogin,
    GroupListView,
    MuserCreateView,
    MuserListView,
    account_edit,
    group_add,
    home,
)
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False), name="index"),
    path("login/", AccountLogin.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", home, name="home"),
    path("account/list/", MuserListView.as_view(), name="account"),
    path("account/add/", MuserCreateView.as_view(), name="account"),
    path("account/edit/", account_edit, name="account"),
    
    path("group/list/", GroupListView.as_view(), name="group"),
    path("group/add/", group_add, name="group"),

]
