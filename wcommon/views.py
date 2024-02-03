from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from wcommon.forms.accountform import AddMuserForm
from wcommon.models import Menu, Muser
from wcommon.references import menu_category


class AccountLogin(LoginView):
    # 覆寫 LoginView 中的 post 方法，以實現自定義的登錄行為
    def post(self, request, *args, **kwargs):
        # 自定義登錄邏輯，例如檢查用戶名和密碼是否符合要求
        username = self.request.POST["username"]
        password = self.request.POST["password"]

        account = authenticate(request, username=username, password=password)
        print(account)
        print(account is not None)
        if account is not None:
            login(request, account)  # 登錄用戶
            return redirect("home")
        else:
            return self.form_invalid(self.get_form())


# @login_required(login_url="/login/")  # 改用攔截器處裡
def home(request):
    # 将查询结果传递给模板
    context = {"allmenu": _get_menu_map(request.user)}
    # 渲染模板并返回响应
    return render(request, "home.html", context)


def _get_menu_map(user: Muser):
    """
    用於取得menu清單
    """
    group = user.group

    if user.is_superuser:
        menu_list = Menu.objects.filter(group__isnull=True).order_by(
            "category", "order"
        )
    # 查询菜单项并构建菜单映射
    else:
        menu_list = Menu.objects.filter(group=group).order_by("category", "order")
    allmenu = []
    group = 0
    i = -1

    for menu in menu_list:
        if group < menu.category:
            allmenu.append({"name": menu_category[menu.category], "list": []})
            group = menu.category
            i += 1
        allmenu[i]["list"].append(menu)
    return allmenu


# 通过装饰器确保用户已登录才能访问此视图
class ItemListView(ListView):
    model = Muser
    template_name = "commmon/item_list.html"
    context_object_name = "musers"

    def get_queryset(self):
        result = Muser.objects
        username_zh = self.request.GET.get("search_username_zh")
        if username_zh:
            result = result.filter(username_zh=username_zh)
        unit = self.request.GET.get("search_unit")
        if unit:
            result = result.filter(unit=unit)
        group = self.request.GET.get("search_group")
        if group:
            result = result.filter(group=group)
        return result.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 将查询条件传递到模板
        context["username_zh"] = self.request.GET.get(
            "search_username_zh", ""
        )  # 如果为None，使用''代替
        context["unit"] = self.request.GET.get(
            "search_unit", ""
        )  # 如果为None，使用''代替
        context["group"] = self.request.GET.get(
            "search_group", ""
        )  # 如果为None，使用''代替

        return context


def account_edit(request):
    if request.method == "GET":
        account = request.GET.get("account")
        username = request.GET.get("username")
        unit = request.GET.get("unit")
        permission_id = request.GET.get("permission")

        # 获取要更新的 Muser 对象
        info = Muser.objects.filter(username=account).first()

        if info:
            # 更新对象的属性
            info.userName_zh = username
            info.unit = unit
            info.permission_id = permission_id
            print(info)
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


class MuserCreateView(CreateView):
    model = Muser
    form_class = AddMuserForm
    template_name = "base/model_edit.html"
    success_url = reverse_lazy(
        "muser-list"
    )  # Redirect to the Muser list view after creation

    def form_valid(self, form):
        """如果表單數據有效，則執行此方法。"""
        print("--------------------------")
        print(form.errors)

        response = super().form_valid(form)
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "success", "redirect_url": self.success_url})
        return response

    def form_invalid(self, form):
        """如果表單數據無效，則執行此方法。"""
        print("--------------------------")
        print(form.errors)
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"status": "error", "errors": form.errors.as_json()}, status=400
            )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 将查询条件传递到模板
        context["action"] = "/account/add/"

        return context
