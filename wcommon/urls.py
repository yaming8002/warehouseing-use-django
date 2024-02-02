from wcommon.views import (
    AccountLogin,
    account_edit,
    account_list,
    home,
)
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False), name="index"),
    path("login/", AccountLogin.as_view(template_name="login.html"), name="login"),
    # path('logout/', AccountLogout.as_view(), name='logout'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("home/", home, name="home"),
    path("account/list/", account_list, name="account"),
    path("account/edit/", account_edit, name="account"),
]


