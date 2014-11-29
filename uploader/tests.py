import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from .models import Image


class TestAuthAPI(TestCase):
    pass


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
