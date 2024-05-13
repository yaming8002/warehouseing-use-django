from wcom.views import (
    AccountLogin,
    AccountLogout,
    CustomPasswordChangeView,
    GroupListView,
    MuserCreateView,
    MuserListView,
    about_sys_view,
    account_edit,
    group_add,
    group_edit,
    home,
)

from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False), name="index"),
    path("login/", AccountLogin.as_view(template_name="login.html"), name="login"),
    path("logout/", AccountLogout.as_view(), name="logout"),
    path("home/", home, name="home"),
    path("about_sys/",about_sys_view,name="about_sys"),
    path("account/list/", MuserListView.as_view(), name="account"),
    path("account/add/", MuserCreateView.as_view(), name="account"),
    path("account/edit/", account_edit, name="account"),
    path('account/change-password/', CustomPasswordChangeView.as_view(), name='change_password'), 

    path("group/list/", GroupListView.as_view(), name="group"),
    path("group/add/", group_add, name="group"),
    path("group/edit/", group_edit, name="group"),

]
