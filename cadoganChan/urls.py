from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^chan/$','cadoganChan.views.index'),
    url(r'^chan/(?P<board>[a-zA-Z]+)/$','cadoganChan.views.board'),
    url(r'^chan/(?P<board_id>[a-zA-Z]+)/(?P<thread_id>[0-9]+)$','cadoganChan.views.thread'),
)
