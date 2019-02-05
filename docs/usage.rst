=====
Usage
=====

Update Your LOCAL APPS
----------------------

To use quartet_4nt4r3s in a project, add it to the bottom of your `LOCAL_APPS` in
your config/settings/base.py module:

.. code-block:: python

    LOCAL_APPS = (
        ...
        'quartet_4nt4r3s.apps.Quartet4nt4r3sConfig',
        ...
    )

Update Your urls.py
-------------------

In your config/urls.py file in the QU4RTET root directory, add the following
code:

.. code-block:: python

    from quartet_4nt4r3s import urls as antares_urls

Then, after the urlpatterns are defined, add this line:

    urlpatterns += antares_urls.urlpatterns

Make Sure You Can Route Traffic Internally
------------------------------------------

The antares package will call serialbox internally and/or using the following
settings:

* ANTARES_SERIALBOX_SCHEME: the URL scheme to use when connecting to the
  serialbox/quartet instance.  Default is `http`.
* ANTARES_SERIALBOX_HOST: the host name of the serialbox/quartet instance to obtain
  numbers from.  Default is `127.0.0.1`.
* ANTARES_SERIALBOX_PORT: the port of the serialbox/quartet instance. This is
  optional.  If you are using non standard http/https ports.

For example, to enable internal http routing on certain operating systems,
you'll need to instruct the webserver to do this.  Below is an example `Nginx`
server configuration section:

.. code-block:: text

    server {
        listen 127.0.0.1:80;
        server_name localhost;
        client_max_body_size 10M;
        location = /favicon.ico { access_log off; log_not_found off; }
        location /static {
            alias /srv/qu4rtet/staticfiles;
        }
        location /media/ {
            root /tmp;
        }
        location / {
            include proxy_params;
            proxy_set_header X-Forwarded-Protocol $scheme;
            proxy_pass http://unix:/srv/qu4rtet/qu4rtet.sock;
        }
    }

Obviously, you'd need to adjust your static and location sections to match
your server configuration.  If you followed the QU4RTET ubuntu installation
instructions, you could use the above section wholesale by including it in
your Nginx config file.
