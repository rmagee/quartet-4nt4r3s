=====
Usage
=====

To use quartet_4nt4r3s in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'quartet_4nt4r3s.apps.Quartet4nt4r3sConfig',
        ...
    )

Add quartet_4nt4r3s's URL patterns:

.. code-block:: python

    from quartet_4nt4r3s import urls as quartet_4nt4r3s_urls


    urlpatterns = [
        ...
        url(r'^', include(quartet_4nt4r3s_urls)),
        ...
    ]
