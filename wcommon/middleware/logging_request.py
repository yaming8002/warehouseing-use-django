from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 在这里记录请求信息
        method = request.method
        path = request.path
        data = request.POST if method == 'POST' else request.GET
        print(f"Request {method} {path}: {data}")

    def process_response(self, request, response):
        # 在这里记录响应信息
        if hasattr(response, 'context'):
            context_data = response.context
            # 在这里处理 context_data，例如打印
            print(f"Context data: {context_data}")
        else:
            print("No context data available.")
        return response

class LogoutOn302Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # 檢查是否是導向到"/home/"的響應，並且狀態碼為302
        if response.status_code == 302:
            logout(request)
            return redirect('login')
        return response