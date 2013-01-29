#/usr/bin/python
# -*- coding: utf-8 -*- 

import os, sys



path = '/home/nazar/django_projects'
if path not in sys.path:
    sys.path.insert(0, '/home/nazar/django_projects/myproject') 

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

