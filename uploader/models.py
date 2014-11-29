import os
import time
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def get_file_name(instance, filename):
    path = time.strftime("images/%Y/%m/%d")
    basename = os.path.basename(filename)

    name = "{name}-{uid}-{unixtime}.{ext}".format(
        name="".join(basename.split(".")[:-1]),  # Remove the extension
        uid=instance.user.id,
        unixtime=time.time(),
        ext=basename.split(".")[-1]
    )
    # Keep the name of the Image object same as the new filename.
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
    RESIZED_IMAGE_NAME = "{name}-{uid}-{unixTime}-{resized_label}.{ext}"

    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to=get_file_name)
    user = models.ForeignKey(User, related_name='uploaded_images')

    @property
    def base_url(self):
        """
        Unique URL for this image.
        """
        pass

    @property
    def resized_image_urls(self):
        """
        Return list of all resized image URLs.
        """
        pass

    def delete(self):
        # Remove the uploaded files from the disk also.
        if os.path.exists(self.image.path):
            os.remove(self.image.path)
        super(Image, self).delete()
