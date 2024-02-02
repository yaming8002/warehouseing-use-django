from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.list import BaseListView
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


@login_required(login_url="/login/")  # 通过装饰器确保用户已登录才能访问此视图
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


@login_required  # 通过装饰器确保用户已登录才能访问此视图
def account_list(request):
    # 获取客户输入的用户名和单位
    username = request.GET.get("username")
    unit = request.GET.get("unit")

    # 创建一个查询集，包含所有的 Muser 记录
    query_set = Muser.objects.all()
    print(query_set)
    # 如果客户提供了用户名，则添加用户名筛选条件
    if username:
        query_set = query_set.filter(userName=username)

    # 如果客户提供了单位，则添加单位筛选条件
    if unit:
        query_set = query_set.filter(unit=unit)

    # 将查询结果传递给模板
    context = {"accounts": query_set}
    context["group_map"] = Group.objects.all()

    # 渲染模板并返回响应
    return render(request, "common/account.html", context)


@login_required  # 通过装饰器确保用户已登录才能访问此视图
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
