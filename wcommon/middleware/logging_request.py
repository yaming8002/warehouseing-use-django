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
        # print(f"Response {response.status_code}: {response.content}")
        return response
