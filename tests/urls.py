# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from quartet_4nt4r3s.urls import urlpatterns as quartet_4nt4r3s_urls

app_name = 'quartet_4nt4r3s'

urlpatterns = [
    url(r'^', include(quartet_4nt4r3s_urls)),
]
