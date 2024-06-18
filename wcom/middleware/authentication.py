from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查请求是否是登录视图，如果是，则不执行中间件逻辑
        if request.path == reverse('login'):  # 根据您的登录视图的URL名称调整
            return self.get_response(request)
        
        # 检查用户是否已登录，如果未登录则重定向到登录页面
        if request.user.is_authenticated:
            if request.user.group_id == 1 or request.user.is_superuser :
                request.session['can_edit'] = True
            else:
                request.session['can_edit'] = False
        else:
            return redirect('/login/')
            # return JsonResponse({'error': '您未登录，请先登录。'}, status=401) # 根据您的登录视图的URL名称调整

        return self.get_response(request)
