from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse

from wcom.models.menu import UserPermissions

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查请求是否是登录视图，如果是，则不执行中间件逻辑
        if request.path == reverse('login'):  # 根据您的登录视图的URL名称调整
            return self.get_response(request)
        # 检查用户是否已登录，如果未登录则重定向到登录页面
        if request.user.is_authenticated:
            meun_permissions = UserPermissions.objects.filter(group__id=request.user.group_id,menu__url = request.path )
            if request.user.is_superuser :
                request.session['u_permission'] = 4
            elif meun_permissions.exists():
                item = meun_permissions.get()
                request.session['u_permission'] = item.permission
            else:
                request.session['u_permission'] = 0
        else:
            return redirect('/login/')
            # return JsonResponse({'error': '您未登录，请先登录。'}, status=401) # 根据您的登录视图的URL名称调整

        return self.get_response(request)
