=============================
quartet_4nt4r3s
=============================

.. image:: https://gitlab.com/lduros/quartet_4nt4r3s/badges/master/coverage.svg
   :target: https://gitlab.com/lduros/quartet_4nt4r3s/pipelines
.. image:: https://gitlab.com/lduros/quartet_4nt4r3s/badges/master/build.svg
   :target: https://gitlab.com/lduros/quartet_4nt4r3s/commits/master
.. image:: https://badge.fury.io/py/quartet_4nt4r3s.svg
    :target: https://badge.fury.io/py/quartet_4nt4r3s

Parsing API for Antares

Documentation
-------------

The full documentation is at https://seriallab.gitlab.io/quartet_4nt4r3s/

Quickstart
----------

Install quartet_4nt4r3s::

    pip install quartet_4nt4r3s

Add it to your `LOCAL_APPS` in QU4RTET's config/settings/base.py:

.. code-block:: python

    LOCAL_APPS = (
        ...
        'quartet_4nt4r3s.apps.Quartet4nt4r3sConfig',
        ...
    )

Add quartet_4nt4r3s's URL patterns to QU4RTET's config/urls.py:

.. code-block:: python

    from quartet_4nt4r3s import urls as antares_urls

    # add it below the main urlpatterns declaration
    urlpatterns = [
        ...
    ]
    urlpatterns += antares_urls.urlpatterns

Features
--------

* Adds an rfXcel emulation layer to QU4RTET, thus enabling an antares or
  any other packaging line to communicate using rfXcel protocols.



