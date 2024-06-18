import logging
import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import redirect, render

from django.utils.translation import gettext_lazy as _

from django.db.models import Q
from wcom.forms.accountform import AddMuserForm, CustomPasswordChangeForm
from wcom.models import Menu, Muser, UserGroup
from wcom.models.menu import SysInfo
from wcom.templatetags import menu_category
from wcom.utils.pagelist import PageListView
from wcom.utils.save_control import SaveControlView

logger = logging.getLogger(__name__)


class AccountLogin(LoginView):
    # 覆寫 LoginView 中的 post 方法，以實現自定義的登錄行為
    def post(self, request, *args, **kwargs):
        # 自定義登錄邏輯，例如檢查用戶名和密碼是否符合要求
        username = self.request.POST["username"]
        password = self.request.POST["password"]

        account = authenticate(request, username=username, password=password)

        if account:
            login(request, account)  # 登錄用戶
            return redirect("home")
        elif Muser.objects.filter(username=username).exists():
            return render(request, "login.html", {"success": False, "msg": "密碼錯誤"})
        else:
            return render(
                request, "login.html", {"success": False, "msg": "帳號不存在"}
            )


class AccountLogout(LogoutView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")


# @login_required(login_url="/login/")  # 改用攔截器處裡
def home(request):
    # 将查询结果传递给模板

    user = request.user

    if user.is_superuser:
        menu_list = Menu.objects.filter(group__isnull=True).order_by(
            "category", "order"
        )
    # 查询菜单项并构建菜单映射
    else:
        menu_list = Menu.objects.filter(group=user.group).order_by("category", "order")
    allmenu = []
    group = 0
    i = -1

    for menu in menu_list:
        if not menu.url:
            continue
        if group < menu.category:
            allmenu.append({"name": menu_category[menu.category], "list": []})
            group = menu.category
            i += 1

        allmenu[i]["list"].append(menu)

    context = {"allmenu": allmenu}
    context["topic"] = SysInfo.get_value(code="0000")
    # 渲染模板并返回响应
    return render(request, "home.html", context)


class MuserListView(PageListView):
    model = Muser
    template_name = "wcom/muser_list.html"
    title_name = "帳號"

    def get_queryset(self):
        query = Q(is_superuser=False)
        username = self.request.GET.get("search_username")
        username_zh = self.request.GET.get("search_username_zh")
        unit = self.request.GET.get("search_unit")
        group = self.request.GET.get("search_group")
        if username:
            query &= Q(username__istartswith=username)
        if username_zh:
            query &= Q(username_zh__istartswith=username_zh)
        if unit:
            query &= Q(unit=unit)
        if group:
            query &= Q(group=group)

        return Muser.objects.filter(query).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_list"] = serializers.serialize(
            "json", UserGroup.objects.filter(is_active=True)
        )

        return context


def account_edit(request):
    if request.method == "GET":
        account = request.GET.get("account")
        username_zh = request.GET.get("username_zh")
        unit = request.GET.get("unit")
        group = UserGroup.objects.filter(id=request.GET.get("group_id")).first()

        # 获取要更新的 Muser 对象
        info = Muser.objects.filter(username=account).first()

        if info:
            # 更新对象的属性
            info.username_zh = username_zh
            info.unit = unit
            info.group = group
            # 保存更新到数据库
            info.save()

            # 返回JSON响应
            response_data = {"success": True, "message": "信息更新成功"}
            return JsonResponse(response_data)
        else:
            response_data = {"success": False, "message": "未找到相应的账户信息"}
            return JsonResponse(response_data)
    else:
        response_data = {"success": False, "message": "仅支持GET请求"}
        return JsonResponse(response_data)


class MuserCreateView(SaveControlView):
    model = Muser
    form_class = AddMuserForm
    template_name = "base/model_edit.html"

    def form_valid(self, form):
        """如果表單數據有效，則執行此方法。"""
        form.save()
        return JsonResponse({"status": "success", "msg": "新增成功"})

    def form_invalid(self, form):
        """如果表單數據無效，則執行此方法。"""
        logger.error("表單數據無效：%s", form.errors)
        return JsonResponse({"status": "error", "msg": form.errors.as_json()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 将查询条件传递到模板
        context["action"] = "/account/add/"
        context["title"] = "新增使用者"

        return context


class GroupListView(PageListView):
    model = UserGroup
    template_name = "wcom/group_list.html"
    title_name = "群組六表"
    # context_object_name = "groups"

    def get_queryset(self):
        result = UserGroup.objects
        name = self.request.GET.get("search_name")
        if name:
            result = result.filter(name__istartswith=name)

        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "權限管控"

        return context


def group_add(request):
    if request.method == "GET":
        context = {"title": "新增權限"}
        context["action"] = "/group/add/"
        context["menus"] = Menu.objects.filter(group__isnull=True).order_by(
            "category", "order"
        )

        context["menu_category"] = menu_category

        return render(request, "wcom/group_menu.html", context)
    else:
        group = UserGroup(name=request.POST.get("group_name"))
        group.save()

        # Loop through the request.POST dictionary
        for key, value in request.POST.items():
            # Check if the key starts with "menu_" to identify menu checkboxes
            if key.startswith("menu_"):
                menu_id = key.split("_")[1]
                try:
                    menu_template = Menu.objects.get(id=menu_id)
                except Menu.DoesNotExist:
                    # 处理模板不存在的情况
                    menu_template = None

                if menu_template:
                    new_menu = Menu.objects.create(
                        name=menu_template.name,
                        url=menu_template.url,
                        category=menu_template.category,
                        order=menu_template.order,
                        group=group,
                    )
                    new_menu.save()

        response_data = {"success": True, "msg": "成功"}
        return JsonResponse(response_data)


def group_edit(request):
    if request.method == "GET":
        context = {"title": "修改權限"}
        context["action"] = "/group/edit/"
        group = UserGroup.objects.filter(id=request.GET.get("id")).first()
        context["menus"] = Menu.objects.filter(group__isnull=True).order_by(
            "category", "order"
        )
        context["menus_acvite"] = (
            Menu.objects.filter(group=group)
            .order_by("category", "order")
            .values_list("name", flat=True)
        )
        context["group"] = group

        return render(request, "wcom/group_menu.html", context)
    else:
        group = UserGroup.objects.get(id=request.POST.get("group_id"))
        group.name = request.POST.get("group_name")
        group.is_active = request.POST.get("group_active") == "on"
        group.save()
        Menu.objects.filter(group=group).delete()
        # Loop through the request.POST dictionary
        for key, value in request.POST.items():
            # Check if the key starts with "menu_" to identify menu checkboxes
            if key.startswith("menu_"):
                menu_id = key.split("_")[1]
                try:
                    menu_template = Menu.objects.get(id=menu_id)
                except Menu.DoesNotExist:
                    # 处理模板不存在的情况
                    menu_template = None

                if menu_template:
                    new_menu = Menu.objects.create(
                        name=menu_template.name,
                        url=menu_template.url,
                        category=menu_template.category,
                        order=menu_template.order,
                        group=group,
                    )
                    new_menu.save()

        response_data = {"success": True, "msg": "成功"}
        return JsonResponse(response_data)


class CustomPasswordChangeView(SaveControlView):
    name = "修改密碼"
    model = Muser
    form_class = CustomPasswordChangeForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(user=request.user)  # 向表单传递当前用户
        context = {
            "title": "修改密碼",
            "action": "/account/change-password/",  # 设置 action 为当前 URL
            "form": form,
        }
        return render(request, "base/model_edit.html", context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            user=request.user, data=request.POST
        )  # 同样，向表单传递当前用户

        if form.is_valid():
            form.save()
            # 处理保存后的逻辑，例如重定向到列表页面
            return JsonResponse({"success": True, "msg": "成功"})

        errors = form.errors.as_json()
        return JsonResponse({"success": False, "msg": f"{errors}"})


def about_sys_view(request):
    # 确定文件路径
    return render(request, "about_sys.html")
