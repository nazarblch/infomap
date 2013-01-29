# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
import cdb
from pymorphy.django_conf import default_morph as morph

def popup(request):
    return render_to_response('tests/popup.html')


def vk(request):
    return render_to_response('tests/vk.html')

def pymorphy(request):
    info = morph.get_graminfo(u'ВАСЯ')

    return HttpResponse(unicode(info[0]['info']))
