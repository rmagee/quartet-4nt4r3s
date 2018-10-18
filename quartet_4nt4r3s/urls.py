# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^rfxcelwss/services/ISerializationServiceSoapHttpPort/?$',
        views.AntaresNumberRequest.as_view(),
        name='antares-number-request'),
    ]
