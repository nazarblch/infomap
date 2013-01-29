from django import template
from django.utils import simplejson

register = template.Library()

@register.filter
def hash(value, arg):
  return value[arg]

@register.filter
def json(object):
  return simplejson.dumps(object)
