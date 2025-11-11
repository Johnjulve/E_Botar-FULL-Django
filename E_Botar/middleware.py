"""
Custom middleware for E-Botar system
"""
from django.utils.deprecation import MiddlewareMixin
from E_Botar.utils.logging_utils import log_activity, get_client_ip


class ActivityLoggingMiddleware(MiddlewareMixin):
    """
    Deprecated: Previously logged page views. Now a no-op to avoid noisy logs.
    """

    def process_request(self, request):
        return None

    def process_response(self, request, response):
        return response


import time

