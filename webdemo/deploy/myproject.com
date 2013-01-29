<VirtualHost *:80>
    # Описание сервера
    ServerAdmin admin@myproject.com
    ServerName myproject.com 

    # Логи
    ErrorLog    /home/nazar/django_projects/myproject/logs/error_log
    CustomLog   /home/nazar/django_projects/myproject/logs/access_log common 

    # wsgi-обработчик (см. ниже)
   WSGIScriptAlias / /home/nazar/django_projects/myproject/deploy/django.wsgi 

    # Параметры запуска wsgi
    WSGIDaemonProcess nazar-site user=nazar group=nazar \




   WSGIProcessGroup nazar-site


    # Статические файлы django-админки
    Alias "/admin_media/"  "/home/nazar/django/contrib/admin/media/"



    <Location "/admin_media/">
        SetHandler None
    </Location>


    # Статические файлы проекта
    Alias "/media/" "/home/nazar/media/"
    <Location "/media/">
        SetHandler None
    </Location>


</VirtualHost>
