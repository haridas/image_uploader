import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files import File
from .models import Image


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
        img = Image()
        img.name = "test1.png"
        img.user = self.user
        img.image = File(open(self.file_name))

        img.save()
        self.assertEqual(img.name, os.path.basename(img.image.name))
        self.assertTrue(os.path.exists(img.image.path))

        img.delete()
        self.assertFalse(os.path.exists(img.image.path))
