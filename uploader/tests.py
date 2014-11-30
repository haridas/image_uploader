"""
@date: 27/Nov/2014
@author: Haridas <haridas.nss@gmail.com>

Active Testcases on this files are -

1. Test authentication API.
2. Test Upload API
3. Test the Core data structure and Image Model's methods.
4. AWS S3 behavior
5. Full Integration Test.
"""
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
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image as PILImage


from django.conf import settings
from .models import Image
from .tasks import FILE_PATH_PARSER


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
    def setUp(self):
        self.upload_url = reverse("upload_image")
        self.auth_url = reverse("authenticate")
        self.auth_data = {
            'username': 'haridas',
            'password': 'haridas'
        }

        self.client = Client()

        self.image = open(os.path.join(os.path.dirname(__file__),
                                       "fixtures/images/me.jpg"), 'rb')

    def test_upload_image(self):
        payload = {
            'auth_token': self._get_auth_token(),
            'image': self.image
        }
        response = json.loads(
            self.client.post(self.upload_url, data=payload).content)

        self.assertTrue(response['success'])
        self.assertTrue(not response['error_msg'])
        self.assertEqual(len(response['image_urls']),
                         len(settings.IMAGE_VARIANTS) + 1)
        self.assertEqual(response['id'], 1)

    def test_error_upload(self):
        payload = {
            'auth_token': self._get_auth_token(),
            'image1': self.image
        }
        response = json.loads(
            self.client.post(self.upload_url, data=payload).content)

        self.assertFalse(response['success'])
        self.assertTrue(response['error_msg'])

    def _get_auth_token(self):
        u = User(username=self.auth_data['username'])
        u.set_password(self.auth_data['password'])
        u.save()

        response = self.client.post(self.auth_url, data=self.auth_data)
        content = json.loads(response.content)
        auth_token = content['auth_token']
        return auth_token


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


class AwsS3Tests(TestCase):
    def setUp(self):
        self.conn = S3Connection(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.S3_IMAGE_BUCKET_NAME
        self.filename = os.path.join(os.path.dirname(__file__),
                                     "fixtures/images/me.jpg")

    def test_bucket_creation_and_access(self):
        try:
            bucket = self.conn.create_bucket(self.bucket_name)
        except Exception as ex:
            print ex

        key = Key(bucket)
        key.key = 'me.jpg'
        key.set_contents_from_filename(self.filename)

        keys = []
        for key in bucket.list():
            keys.append(key.name)

        self.assertTrue(key.key in keys)


#
# Kinda full integration test to cover all the components of the system.
#
class FullIntegrationTest(TestCase):
    def setUp(self):
        self.upload_url = reverse("upload_image")
        self.auth_url = reverse("authenticate")
        self.auth_data = {
            'username': 'haridas',
            'password': 'haridas'
        }

        self.client = Client()

        self.filename = os.path.join(os.path.dirname(__file__),
                                     "fixtures/images/me.jpg")

        self.image = open(self.filename, 'rb')

        # S3 Configurations Details.
        self.conn = S3Connection(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.S3_IMAGE_BUCKET_NAME

    def test_upload_api_and_cloud_syncing(self):
        """
        End-to-End Testing.
        """
        payload = {
            'auth_token': self._get_auth_token(),
            'image': self.image,
            'async_operation': 'false'
        }

        response = json.loads(
            self.client.post(self.upload_url, data=payload).content)

        # Logger file got updated after the image upload.
        self.logger_size_before = os.path.getsize(os.path.join(
            settings.BASE_DIR, "logs/image_resize.log"))

        # Check created images are being generated as per the specificatioin.
        self.image_variants = dict([(a[0],
                                     a[1]) for a in settings.IMAGE_VARIANTS])

        self._check_api_response(response)
        self._check_image_resize_operation(response)
        self._check_image_logger_operation(response)
        self._check_could_syncing_operation(response)

    def _check_api_response(self, response):
        self.assertTrue(response['success'])

    def _check_image_resize_operation(self, response):
        for name, img in response['image_urls'].iteritems():
            img_file = os.path.join(settings.MEDIA_ROOT, img)

            # File exists or not test
            self.assertTrue(os.path.exists(img_file))

            # Check the resize operation was done properly.
            if name != Image.IMG_LABEL:
                self.assertTrue(
                    PILImage.open(img_file).size == self.image_variants.get(
                        name))

    def _check_image_logger_operation(self, response):
        curr_size = os.path.getsize(os.path.join(
            settings.BASE_DIR, "logs/image_resize.log"))

        print curr_size, self.logger_size_before

        # Checking that the logger got updated via its modification time.
        # self.assertTrue(curr_size > self.logger_size_before)

        # TODO: Since there is disk buffering effect the size or time change
        # may not be sync on time, so we can't test the file change using time
        # or size change of the logfile effectively. Find some alternate.

    def _check_could_syncing_operation(self, response):
        bucket = self.conn.create_bucket(self.bucket_name)

        file_list = [key.name for key in bucket.list()]

        img_file = ["/".join(FILE_PATH_PARSER.findall(
            os.path.join(settings.MEDIA_ROOT, img))[0])
            for img in response['image_urls'].values()]

        print set(file_list).issuperset(set(img_file))

    def _get_auth_token(self):
        u = User(username=self.auth_data['username'])
        u.set_password(self.auth_data['password'])
        u.save()

        response = self.client.post(self.auth_url, data=self.auth_data)
        content = json.loads(response.content)
        auth_token = content['auth_token']
        return auth_token
