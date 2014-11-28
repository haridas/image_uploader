import json
import functools

from django.utils import timezone
from django.http import HttpResponse
from django.utils.module_loading import import_string
from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY
from django.conf import settings


def validate_auth_token(view):

    def _check_token(self, request, *args, **kwargs):

        auth_token = request.POST['auth_token']

        if auth_token:
            session = import_string(settings.SESSION_ENGINE).SessionStore(
                auth_token)

            # Token should be a valid one.
            if (SESSION_KEY in session and session.get_expiry_date() > timezone.now()):
                return view(self, request, *args, **kwargs)

        # All other cases means the auth token expired or invalid.
        result = {
            'success': False,
            'error_msg': ("Auth Token is invalid or expired. Please get new "
                          "Auth token to use this API.")
        }
        return HttpResponse(json.dumps(result),
                            content_type="application/json")

    return _check_token


class ValidateAuthToken(object):
    """
    Decorator which check method's should have a valid backend auth token to
    interact with the API.
    """

    def __init__(self, fun):
        self.fun = fun

    @functools.wraps
    def __call__(self, request, *args,  **kwargs):

        auth_token = request.POST.get('auth_token')

        if auth_token:
            session = import_string(settings.SESSION_ENGINE).SessionStore(
                auth_token)

            # Token should be a valid one.
            if session.get_expiry_date() > timezone.now():
                return self.fun(self, request, *args, **kwargs)

        # All other cases means the auth token expired or invalid.
        result = {
            'success': False,
            'error_msg': ("Auth Token is invalid or expired. Please get new "
                          "Auth token to use this API.")
        }
        return HttpResponse(json.dumps(result),
                            content_type="application/json")
