from django.conf.urls import patterns, include, url
from django.contrib import admin
from uploader.views import UploaderView, AuthView, CatchAllView

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authenticate/', AuthView.as_view(), name="authenticate"),
    url(r'^upload/', UploaderView.as_view(), name="upload_image"),
    # TODO: url(r'^.*$/', CatchAllView.as_view(), name="catch_all")
)
