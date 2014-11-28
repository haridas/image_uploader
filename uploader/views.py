import json

from django.views.generic import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils.module_loading import import_string
from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY
from django.conf import settings
from .utils import ValidateAuthToken, validate_auth_token


class AuthView(View):
    """
    Exposes a token based Authentication system to make it fully stateless
    REST compatible system.
    """
    def post(self, request, *args, **kwargs):
        """
        Check the given username and password parameters on the POST request
        is valid, if so generate a token for further communication.
        """
        result = {
            'auth_token': '',
            'success': True,
            'error_msg': None
        }

        try:
            username = request.POST['username']
            password = request.POST['password']
        except KeyError:
            result['success'] = False
            result['error_msg'] = (" Please provide `username` and `password`"
                                   " as POST request parameters.")
            return HttpResponse(json.dumps(result),
                                content_type="application/json")

        # Authenticate the username and password with the user db and geneate
        # a session token for future transactions.
        user = User.objects.filter(username=username)[:1]

        if user:
            user = user[0]
            if user.check_password(password):

                # Generate A token for this user.
                session_key = request.POST.get('auth_token', None)

                session = import_string(settings.SESSION_ENGINE).SessionStore(
                    session_key)

                session[SESSION_KEY] = user.pk
                session[HASH_SESSION_KEY] = user.get_session_auth_hash()
                session.save()
                result['auth_token'] = session.session_key

            else:
                result['success'] = False
                result['error_msg'] = (" Authentication Failed")

        else:
            result['success'] = False
            result['error_msg'] = (" Username doesn't exists.")

        return HttpResponse(json.dumps(result),
                            content_type="application/json")

    def _generate_token(self):
        pass


class UploaderView(View):
    """
    Handles the Image upload operations and send the response to the client
    right after receiving the request from the client.
    """
    @validate_auth_token
    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request.
        """
        return HttpResponse(content='{}', content_type="application/json")
