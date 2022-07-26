from django.conf import settings
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from ipware import get_client_ip


class HealthCheckMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_allowed = []

    def __call__(self, request: HttpRequest):
        client_ip, is_routable = get_client_ip(request)
        if is_routable and client_ip in self.ip_allowed:
            settings.DEBUG = True
        else:
            settings.DEBUG = True

        if request.method == "GET" and (
            request.path == "/" or request.path == "/HealthCheck"
        ):
            return HttpResponse("200")
        elif request.path.startswith("/auth/") and request.headers.get("Authorization"):
            raise Exception("This operation is not allowed!")
        elif request.path.startswith("/dashboard/") and not request.headers.get(
            "Authorization"
        ):
            raise Exception("This operation is not allowed!")

        response = self.get_response(request)

        return response
