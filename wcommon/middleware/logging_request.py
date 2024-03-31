from django.utils.deprecation import MiddlewareMixin

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
