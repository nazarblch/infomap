#!/usr/bin/python

import os
import sys

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(SITE_ROOT, "..")
if path not in sys.path:
  sys.path.append(path)
path = SITE_ROOT
if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
