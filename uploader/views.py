import json
import tempfile
import logging

from django.views.generic import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.files import File
from django.utils.module_loading import import_string
from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY
from django.db import DatabaseError
from django.conf import settings
from .utils import validate_auth_token
from .models import Image
from .tasks import resize_images

logger = logging.getLogger(__name__)


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
            logger.exception("Arguments are invalid.")

            result['success'] = False
            result['error_msg'] = (" Please provide `username` and `password`"
                                   " as POST request parameters.")
            return HttpResponse(json.dumps(result),
                                content_type="application/json")

        # Authenticate the username and password with the user db and generate
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

                # TODO: Add proper cleanup operations of stale tokens.

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

        payload_format = {
            'image': <fileobject>,
            'auth_token': <str>,
            'async_operation': True/False (Default: True)
        }
        """
        data = {
            'id': None,
            'success': False,
            'error_msg': None,
            'image_urls': {}
        }

        # Save the uploaded image on to temporary location.
        try:
            im = request.FILES['image']

            # A flag to turn on or of asynchronous nature of this API,
            # can be usefull to test the entire system effectively
            async_operation = json.loads(request.POST.get('async_operation',
                                                          'true'))
        except KeyError:
            data['error_msg'] = "Attribute `image` doesn't exists."
            return HttpResponse(content=json.dumps(data),
                                content_type="application/json")
        else:
            if im.multiple_chunks():
                # preserve the original name.
                name = im.name
                full_im = self._save_file_on_temp_loc(im)
                im = File(full_im)
                im.name = name
            else:
                im = File(im)

        # Create new Image object.
        try:
            image = Image()
            image.image = im
            image.user = request.user
            image.save()

            # All looks fine.. prepare correct set of data.
            data['image_urls'] = image.resized_image_urls
            data['id'] = image.id
            data['success'] = True

            # place the image resize job background using celery tasks.
            async_operation and resize_images.delay(
                image.resized_image_paths, image.IMG_LABEL)

            # Do all operation synchronously.
            not async_operation and resize_images(
                image.resized_image_paths, image.IMG_LABEL, async_operation)

        except DatabaseError as ex:
            data['error_msg'] = ("Error while saving on the Database "
                                 " - {}".format(ex.message))

        return HttpResponse(content=json.dumps(data),
                            content_type="application/json")

    def _save_file_on_temp_loc(self, image):
        tp = tempfile.NamedTemporaryFile()
        for chunk in image.chunks():
            tp.write(chunk)
        return tp


class CatchAllView(View):
    pass
