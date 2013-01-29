# -*- coding: utf-8 -*-

from django import template
from django.utils import simplejson

register = template.Library()


@register.filter
def hash(value, arg):

    if not value.has_key(arg):
        arg  = int(arg)

    return value[arg]

@register.filter
def has_key(value, arg):
    if  value.has_key(arg) : return True
    if  value.has_key(str(arg)) : return True
    return False






@register.filter
def json(object):
    return simplejson.dumps(object)

@register.filter
def split(str,splitter):
    return str.split(splitter)


@register.filter
def name(model_obj):

    return u'%s' %  model_obj.get_name()


@register.filter
def subarr(arr, l):

    return arr[:l]

