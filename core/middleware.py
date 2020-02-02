from rest_framework import status
from rest_framework.response import Response
from django.utils.deprecation import MiddlewareMixin


class ResponseCustomMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        if not response.is_rendered and isinstance(response, Response):
            if not response.data:
                response.data = {}
            if "data" not in response.data:
                response.data = {"data": response.data}
            # you can add you logic for checking in status code is 2** or 4**.
            response.data.setdefault("success", status.is_success(response.status_code))
            response.data.setdefault("status_code", response.status_code)
        return response
