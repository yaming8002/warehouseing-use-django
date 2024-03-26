from wcommon.views import (
    AccountLogin,
    AccountLogout,
    GroupListView,
    MuserCreateView,
    MuserListView,
    account_edit,
    group_add,
    group_edit,
    home,
)

from django.urls import path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False), name="index"),
    path("login/", AccountLogin.as_view(template_name="login.html"), name="login"),
    path("logout/", AccountLogout.as_view(), name="logout"),
    path("home/", home, name="home"),
    path("account/list/", MuserListView.as_view(), name="account"),
    path("account/add/", MuserCreateView.as_view(), name="account"),
    path("account/edit/", account_edit, name="account"),
    path("group/list/", GroupListView.as_view(), name="group"),
    path("group/add/", group_add, name="group"),
    path("group/edit/", group_edit, name="group"),
]
