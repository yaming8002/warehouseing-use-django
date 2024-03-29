import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from wcommon.forms.accountform import AddMuserForm
from wcommon.models import Menu, Muser, UserGroup
from wcommon.templatetags import menu_category
from wcommon.utils.pagelist import PageListView

logger = logging.getLogger(__name__)


class AccountLogin(LoginView):
    # 覆寫 LoginView 中的 post 方法，以實現自定義的登錄行為
    def post(self, request, *args, **kwargs):
        # 自定義登錄邏輯，例如檢查用戶名和密碼是否符合要求
        username = self.request.POST["username"]
        password = self.request.POST["password"]

        account = authenticate(request, username=username, password=password)
        
        if account is not None:
            login(request, account)  # 登錄用戶
            return redirect("home")
        elif Muser.objects.filter(username=username).exists():
            return render(request, "login.html", {"success": False, "msg": "密碼錯誤"}) 
        else :
            return render(request, "login.html", {"success": False, "msg": "帳號不存在"}) 


class AccountLogout(LogoutView):
    def post(self, request, *args, **kwargs):
        
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
    context['topic'] ="國廣林口倉庫系統"
    # 渲染模板并返回响应
    return render(request, "home.html", context)


class MuserListView(PageListView):
    model = Muser
    template_name = "wcommmon/muser_list.html"
    title_name = "帳號"

    def get_queryset(self):
        result = Muser.objects
        username = self.request.GET.get("search_username")
        if username:
            result = result.filter(username__istartswith=username)

        username_zh = self.request.GET.get("search_username_zh")
        if username_zh:
            result = result.filter(username_zh__istartswith=username_zh)

        unit = self.request.GET.get("search_unit")
        if unit:
            result = result.filter(unit=unit)

        group = self.request.GET.get("search_group")
        if group:
            result = result.filter(group=group)
        return result.all()

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


class MuserCreateView(CreateView):
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
    template_name = "wcommon/group_list.html"
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

        return render(request, "wcommon/group_menu.html", context)
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

        
        return render(request, "wcommon/group_menu.html", context)
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

from bs4 import BeautifulSoup
from openpyxl import Workbook


def export_html_table_to_excel(request):
    html_content = request.GET.get('html_content')
    output_file = request.GET.get('output_file')
    # 解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    # 创建一个新的Excel工作簿
    wb = Workbook()
    ws = wb.active

    # 遍历HTML表格中的行和单元格，并将数据写入Excel工作表
    for i, row in enumerate(table.find_all('tr')):
        for j, cell in enumerate(row.find_all(['th', 'td'])):
            ws.cell(row=i + 1, column=j + 1, value=cell.get_text())

    # 保存Excel文件
    wb.save(output_file)

import csv

from django.http import HttpResponse


def export_data_to_excel(data, output_file, column_names):
    # 创建一个HttpResponse对象，指定内容类型为Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{output_file}"'

    # 使用csv库将数据写入HttpResponse对象
    writer = csv.writer(response)

    # 写入列标题
    writer.writerow(column_names)

    # 写入数据
    for row in data:
        writer.writerow(row)

    return response