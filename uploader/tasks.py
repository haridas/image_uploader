"""
These tasks are supposed to be running on different machines. Those machiens
may or maynot have access to the main database. But the file storage is
accesible across network.

So we send messages with enough meta data to process the specified tasks. Make
sure that we won't sent any unnecessary data through Broker for better
performance.
"""
from __future__ import absolute_import

from celery import shared_task
from PIL import Image
import logging

# Normal logger, can be used with all other moduels log in pythonic way.
logger = logging.getLogger(__name__)

# Custom logger for logging image operations specifically.
img_logger = logging.getLogger("log_img_operations")


@shared_task(routing_key="resize_image")
def resize_images(image_map, orginal_key):
    """
    Resize the given set of images into specified targets. Resize and save it
    on the disk.

    Also log these resizing activity asynchronously.

    :param image_map: Return value from
                      class:~`uploader.models.Image.resized_image_paths`

    :param orginal_key: Name of the key on the map which hold the details of
                        original image's size and absolute location.

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
def logger_task(log_level, message):
    """
    Logging task. Main job is to keep track of all activities happening
    on different components of the system. All other components sends messages
    in standard format for logging.

    :param log_level: Logger level. eg; INFO, ERROR, WARNING
    :param message: str, the message to be logged.
    """
    if hasattr(img_logger, log_level.lower()):
        getattr(img_logger, log_level.lower())(message)
    else:
        # Invalid log_level.
        img_logger.warning("Log level given '{}' is invalid".format(log_level))


@shared_task(routing_key="cdn_sync")
def sync_images_to_cdn(images):
    """
    A background task which will push the locally saved images to cloud for
    reduendency and easy access via CDNs.
    """
    pass
