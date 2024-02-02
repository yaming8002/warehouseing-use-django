from django.http import HttpResponseForbidden


class DenyMapFilesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.endswith(".map"):
            return HttpResponseForbidden("Access to .map files is forbidden")
        return self.get_response(request)
