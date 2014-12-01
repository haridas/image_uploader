Image Uploader App
==================

A full scale Asynchronous image upload and cloud syncing application.

Main components are - 

1. Authentication API which generate Auth token for future communication.
2. Image Uploader Rest API.
3. Background task for resizing the images.
4. Dedicated Logger task to aggregate the logging data into one server.
5. CDN or Cloud syncing script with retry option.

We are using celery to do the asynchronous also in the same time we are getting
the multi processing ability. Also provided synchronous uploader API option, 
which will disable all background operation and does everything synchronously.
Very helpful for writing integration test cases also run entire thing on
a single machine.

Right now I'm using my S3 account to sync the images.

How To Install
==============
Setup your own virtualenv and use requirements.txt file provided with this
project.

$ pip install -r requirements.txt


How To Test
===========

To test the  application you don't need to run any server or celery. It all are
configured synchronously and I'm using django's inbuilt http Client to create
HTTP request.

Run this command to test the codebase.

$ python manage.py test


HOW To Run
==========

We need to services :- 

1. Http Server, 

    $ python manage.py runserver

2. Celery worker pool.

   Run bellow command from the root project folder.

   $ celery -A image_uploader worker -l info

After this your are ready to go with sending requests to Auth or Image Uploader
APIs. You can use cURL or Chrome Postman plugin or UnitTest written on the
tests.py file of `uploader` application.

To get a auth token for communication.

$ curl -i -F password=haridas -F username=haridas http://localhost:8000/authenticate/

To upload a file using cURL command:-

$ curl -i -F auth_token=fvu53jeu5y5w1khspc9i32i9ht75jd71 -F image=@/home/haridas/me.jpg http://localhost:8000/upload/


