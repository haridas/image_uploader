"""
These tasks are supposed to be running on different machines. Those machiens
may or maynot have access to the main database. But the file storage is
accesible across network.

So we send messages with enough meta data to process the specified tasks. Make
sure that we won't sent any unnecessary data through Broker for better
performance.

All the asynchronous tasks takes a special argument 'async_operation', a
boolean flag which further decides to spwan async or synchronous job.
"""
from __future__ import absolute_import
import re
import os

from celery import shared_task
from PIL import Image
import logging
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.conf import settings

# Normal logger, can be used with all other moduels log in pythonic way.
logger = logging.getLogger(__name__)

# Custom logger for logging image operations specifically.
img_logger = logging.getLogger("log_img_operations")

# Used to extract Year, Month, day from the file name, so we can create S3 key
# properly.
FILE_PATH_PARSER = re.compile('^.*\/([0-9]{4})\/([0-9]{2})\/([0-9]{2}).*$')


@shared_task(routing_key="resize_image")
def resize_images(image_map, orginal_key, async_operation=True):
    """
    Resize the given set of images into specified targets. Resize and save it
    on the disk.

    Also log these resizing activity asynchronously.

    :param image_map: Return value from
                      class:~`uploader.models.Image.resized_image_paths`

    :param orginal_key: Name of the key on the map which hold the details of
                        original image's size and absolute location.

    :param async_peration: Flag which to turn off any asynchronous operation
                           done by this task. By default it is enabled.

    """
    if image_map:

        orginal_img_meta = image_map.pop(orginal_key)
        orginal_img = Image.open(orginal_img_meta['path'])

        for sub_imgs in image_map.values():
            _copy_org_img = orginal_img.copy()
            _copy_org_img.resize(sub_imgs['size'])
            _copy_org_img.save(sub_imgs['path'])

            # Log the action.
            log_msg = ("New resized image with dimension: {size} - (wxh)"
                       " At loc: {path} has been generated from: {org_img}")
            logger_task.delay("INFO", log_msg.format(
                size=sub_imgs['size'], path=sub_imgs['path'],
                org_img=orginal_img_meta['path']))

        # Push these images to CDN via background process.
        sync_images_to_cdn.delay(image_map)


@shared_task(routing_key="logger")
def logger_task(log_level, message, async_operation=True):
    """
    Logging task. Main job is to keep track of all activities happening
    on different components of the system. All other components sends messages
    in standard format for logging.

    :param log_level: Logger level. eg; INFO, ERROR, WARNING
    :param message: str, the message to be logged.
    :param async_peration: Flag which to turn off any asynchronous operation
                           done by this task. By default it is enabled.
    """
    if hasattr(img_logger, log_level.lower()):
        getattr(img_logger, log_level.lower())(message)
    else:
        # Invalid log_level.
        img_logger.warning("Log level given '{}' is invalid".format(log_level))


@shared_task(routing_key="cdn_sync", bind=True, async_operation=True)
def sync_images_to_cdn(self, images):
    """
    A background task which will push the locally saved images to cloud for
    reduendency and easy access via CDNs.

    :param images: Return value from
                    class:~`uploader.models.Image.resized_image_paths`

    :param async_peration: Flag which to turn off any asynchronous operation
                           done by this task. By default it is enabled.
    """
    try:
        conn = S3Connection(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        bucket = conn.create_bucket(settings.S3_IMAGE_BUCKET_NAMES)

        for image in images.values():
            key = Key(bucket)

            # format: yyyy/mm/dd/<file-name>
            key_name = os.path.join("/".join(
                FILE_PATH_PARSER.findall(image['path'])[0]),
                os.path.basename(image['path']))

            key.name = key_name
            key.set_contents_from_filename(image['path'])

    except (boto.exception.AWSConnectionError,
            boto.exception.BotoClientError,
            boto.exception.S3ResponseError) as ex:
        # These are the known errors, we retry for these errors.
        logger.exception("Error while uploading the images.. retrying...")

        # Retry the job after given delay and only try up to max retry limit.
        raise self.retry(exc=ex,
                         max_retries=settings.TASK_MAX_RETRIES,
                         countdown=settings.TASK_RETRY_DELAY)
    except Exception:
        # Unknown error occurred, Could be due to MaxRetriesExceptionError.
        logger.exception("Unknown Error. Please check...")
