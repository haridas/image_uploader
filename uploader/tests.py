import os
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import SESSION_KEY
from django.utils.module_loading import import_string
from django.utils import timezone
from django.core.files import File
from django.test import TestCase
from django.test import Client


from django.conf import settings
from .models import Image


class TestAuthAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_url = reverse("authenticate")
        self.auth_data = {
            'username': 'haridas',
            'password': 'haridas'
        }

    def test_auth_failure(self):
        response = self.client.post(self.auth_url, data=self.auth_data)

        content = json.loads(response.content)
        self.assertTrue(response.status_code == 200)
        self.assertFalse(content['success'])  # No User created yet.

    def test_auth_success(self):

        self._create_user()

        response = self.client.post(self.auth_url, data=self.auth_data)
        content = json.loads(response.content)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(content['success'])

    def test_authentication_using_auth_token(self):
        user = self._create_user()
        response = self.client.post(self.auth_url, data=self.auth_data)
        content = json.loads(response.content)
        auth_token = content['auth_token']

        session = import_string(
            settings.SESSION_ENGINE).SessionStore(auth_token)

        self.assertTrue(session.get_expiry_date() > timezone.now())
        self.assertTrue(SESSION_KEY in session)
        self.assertTrue(session[SESSION_KEY] == user.pk)

        # Check auth_toekn is valid on backend itself.

    def test_api_with_junk_data(self):
        self._create_user()
        self.auth_data['username'] = 'haridas1'
        response = self.client.post(self.auth_url, data=self.auth_data)
        content = json.loads(response.content)
        self.assertFalse(content['success'])

    def _create_user(self):
        u = User(username=self.auth_data['username'])
        u.set_password(self.auth_data['password'])
        u.save()
        return u


class TestUploadAPI(TestCase):
    pass


class TestImageModel(TestCase):

    def setUp(self):

        self.user = User()
        self.user.username = "haridas"
        self.user.set_password("haridas")
        self.user.save()

        self.file_name = os.path.join(os.path.dirname(__file__),
                                      "fixtures/images/me.jpg")

    def test_create_new_image(self):
        """
        Test creation of new image.
        """
        img = self._create_new_img()
        self.assertEqual(img.name, os.path.basename(img.image.name))
        self.assertTrue(os.path.exists(img.image.path))
        img.delete()

    def test_image_delete(self):
        """ Test Image delete and cleanup opeation"""
        img = self._create_new_img()
        img.delete()
        self.assertFalse(os.path.exists(img.image.path))

    def test_resized_image_urls(self):
        """ Test the validity of the resized image urls."""
        img = self._create_new_img()
        self.assertEqual(len(img.resized_image_urls),
                         len(settings.IMAGE_VARIANTS) + 1)

        img.delete()

    def test_resized_image_path(self):
        """ Check all image paths exists """
        img = self._create_new_img()
        resized_img_paths = img.resized_image_paths

        for resized in settings.IMAGE_VARIANTS:
            self.assertTrue(resized[0] in resized_img_paths)

    def test_resized_img_creation(self):
        img = self._create_new_img()
        img.delete()

    def _create_new_img(self):
        img = Image()
        img.name = "test1.png"
        img.user = self.user
        img.image = File(open(self.file_name))
        img.save()
        return img
