# middleware.py 或者你项目的任何合适位置

from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # 检查请求的路径是否是登录页面或其他不需要登录的路径
            if not request.path.startswith(reverse('login')) and  not request.path.startswith(reverse('logout')) and  not request.path.startswith(settings.STATIC_URL):
                return redirect('/logout/')
                # return JsonResponse({'error': '您以登出，請重新登入'}, status=401) # 根据您的登录视图的URL名称调整
        return self.get_response(request)
