import os
import re
import time
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


def get_file_name(instance, filename):

    # Heirarchial storage of image, helps to manage the files in a directory
    # or migrate old files to systems with slower IO etc..
    path = time.strftime("images/%Y/%m/%d")
    basename = os.path.basename(filename)

    # NOTE: Right now we are using Time based naming. A single user can upload
    # 10^10 images per second. If we are using UUID this will be time agnostic
    # and more precise, we don't need to worry much about sync server time.
    name = "{name}-{uid}-{unixtime}.{ext}".format(
        name="".join(basename.split(".")[:-1]),  # Remove the extension
        uid=instance.user.id,
        unixtime="".join(('%.10f' % time.time()).split(".")),
        ext=basename.split(".")[-1]
    )

    # Keep the name of the Image object same as the newslc514461
    # filename.
    instance.name = name

    fullpath = os.path.join(path, name)
    return fullpath


class Image(models.Model):
    """
    Model which hold the meta information about the uploaded image on DB.
    """
    # Image nameing convention.
    #
    # Base Image name with URL has the following naming structure.
    # Original -> {name}-{uid}-{unixTime}.{ext}
    # Resized  -> {name}-{uid}-{unixTime}-{resize_lable}.{ext}
    #
    BASE_NAME = "{name}-{uid}-{unixTime}.{ext}"
    BASE_NAME_PARSER = re.compile('([\w\W\d]+)\-([\d]+)\-([\d]+)\.([\w\W]+)')

    RESIZED_IMAGE_NAME = "{name}-{uid}-{unixtime}-{resized_label}.{ext}"

    # The image label given for the original uploaded image.
    IMG_LABEL = "original"

    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to=get_file_name)
    user = models.ForeignKey(User, related_name='uploaded_images')

    @property
    def resized_image_urls(self):
        """
        Return list of all resized image URLs. The Target images may not be
        created yet.

        :return: Map of image_label -> Image URL
        :rtype: dict
        """
        # A naive caching.
        if hasattr(self, '_resized_image_urls'):
            return self._resized_image_urls
        else:
            image_urls = {
                self.IMG_LABEL: self.image.url
            }

            for resized in settings.IMAGE_VARIANTS:

                image_urls[resized[0]] = os.path.join(
                    os.path.dirname(self.image.path),
                    self.get_resized_image_names(self.name, resized[0]))

            self._resized_image_urls = image_urls
            return image_urls

    @property
    def resized_image_paths(self):
        """
        From the original image, generate given set of resized images.

        :return: Map of image_label -> { size: (width, height),
                                         path: absolute_image_path}
        :rtype: dict
        """
        # A naive caching.
        if hasattr(self, '_resized_image_paths'):
            return self._resized_image_paths
        else:
            image_abs_paths = {
                self.IMG_LABEL: {
                    "size": (self.image.width, self.image.height),
                    "path": self.image.path
                }
            }

            for resized in settings.IMAGE_VARIANTS:

                image_abs_paths[resized[0]] = {
                    "path": os.path.join(
                        os.path.dirname(self.image.path),
                        self.get_resized_image_names(self.name, resized[0])
                    ),
                    "size": resized[1]
                }

            self._resized_image_paths = image_abs_paths
            return image_abs_paths

    @classmethod
    def get_resized_image_names(cls, org_name, label_name):
        """
        Generate image name with given label.
        :param label_name: Tag name for resized image.
        :return: Original image name with this label.
        :rtype: str
        """
        org_filename, user_id, timestamp, ext = cls.BASE_NAME_PARSER.findall(
            org_name)[0]
        return cls.RESIZED_IMAGE_NAME.format(
            name=org_filename, uid=user_id, unixtime=timestamp,
            resized_label=label_name, ext=ext)

    def delete(self):
        # Remove the uploaded files from the disk also.
        if os.path.exists(self.image.path):
            os.remove(self.image.path)
        super(Image, self).delete()
