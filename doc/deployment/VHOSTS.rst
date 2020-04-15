Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess objects-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/objects/log/apache2/error.log"
        CustomLog "/srv/sites/objects/log/apache2/access.log" common

        WSGIProcessGroup objects-<target>

        Alias /media "/srv/sites/objects/media/"
        Alias /static "/srv/sites/objects/static/"

        WSGIScriptAlias / "/srv/sites/objects/src/objects/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-objects-<target>]
    user = <user>
    command = /srv/sites/objects/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/objects/src/objects/wsgi/wsgi_<target>.py
    home = /srv/sites/objects/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/objects/log/uwsgi_err.log
    stdout_logfile = /srv/sites/objects/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_objects_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/objects/log/nginx-access.log;
      error_log /srv/sites/objects/log/nginx-error.log;

      location /500.html {
        root /srv/sites/objects/src/objects/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/objects/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/objects/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_objects_<target>;
      }
    }
