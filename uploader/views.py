import json

from django.views.generic import View
from django.http import HttpResponse
from django.contrib.auth.models import User


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
        import pdb; pdb.set_trace()
        result = {
            'token': '',
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
                result['token'] = 'testToken'
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

    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request.
        """
        return HttpResponse(content='{}', content_type="application/json")
