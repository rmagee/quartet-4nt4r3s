=====
Usage
=====

To use quartet_4nt4r3s in a project, add it to the bottom of your `LOCAL_APPS` in
your config/settings/base.py module:

.. code-block:: python

    LOCAL_APPS = (
        ...
        'quartet_4nt4r3s.apps.Quartet4nt4r3sConfig',
        ...
    )

In your config/urls.py file in the QU4RTET root directory, add the following
code:

.. code-block:: python

    from quartet_4nt4r3s import urls as antares_urls

Then, after the urlpatterns are defined, add this line:

    urlpatterns += antares_urls.urlpatterns

