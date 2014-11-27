from django.conf.urls import patterns, include, url
from django.contrib import admin
from uploader.views import UploaderView, AuthView

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^authenticate/', AuthView.as_view()),
    url(r'^upload/', UploaderView.as_view())
)
