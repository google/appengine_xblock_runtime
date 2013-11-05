XBlock Runtime for Google App Engine
====================================

A library that provides an XBlock runtime environment which uses the Google App
Engine datastore.


Dependencies
------------

In addition to App Engine itself, this relies on edX's XBlock_ project.


Running the example application locally
---------------------------------------

The library is bundled with a simple App Engine application which enables a user
to:

    * Install a XBlock usage from a snippet of XML

    * View and interact with the given XBlock

To run the application on common Linux distributions, execute:

::

    sh ./scripts/run_example.sh

This will install all the dependencies and start the server. If this script
cannot be run on your platform, follow the steps below:

    1. Download the XBlock_ repo from GitHub into the ``examples/lib/`` folder.
       For consistency, you should check out commit
       ``2daa4e541c1613a703262c9dcd6be9c1928b1299``.

    2. In the ``examples/lib/XBlock`` folder, execute:
       ``python setup.py egg_info``

    3. In the ``examples/lib/XBlock/thumbs`` folder, execute:
       ``python setup.py egg_info``

    4. Create a folder ``examples/lib/appengine_xblock_runtime`` and copy
       ``appengine_xblock_runtime`` and ``setup.py`` into it.

    5. In ``examples/lib/appengine_xblock_runtime`` execute:
       ``python setup.py egg_info``

    6. Start the App Engine development server in the ``examples/`` folder:
       ``PATH_TO_GAE_SDK/dev_appserver.py .``


Running the example application on production App Engine
--------------------------------------------------------

To install on production App Engine, follow the steps above and then:

    1. Create a new application on App Engine (https://appengine.google.com/)
       with a name that matches the application name in ``app.yaml``
       (e.g. 'xblock-example')

    2. Deploy with the command ``$APP_ENGINE_SDK/appcfg.py update .``


Running tests
-------------

To run the tests on common Linux distributions, execute:

::

    sh ./scripts/tests.sh

If this script cannot be run on your platform, follow the steps in _`Examples`. 
Ensure that the following packages are on your ```PYTHONPATH``:

    * The App Engine SDK

    * WebOb (available the ```lib`` folder in the App Engine SDK)

    * XBlock

To run the test suite: ``nosetests tests``


Using this library in your own App Engine app
---------------------------------------------

To use the library in a Google App Engine application, you should follow these
steps:

    1. Create a ``lib/`` folder in your application.

    2. Download the XBlock_ repo from GitHub into your ``lib/`` folder.

    3. In the ``lib/XBlock`` folder, execute:
       ``python setup.py egg_info``

    4. Download this runtime package into your ``lib/`` folder.

    5. In the ``lib/appengine_xblock_runtime`` folder, execute:
       ``python setup.py egg_info``

    6. Register the two packages by including in your application code:
       ``pkg_resources.working_set.add_entry(`` *path_to_XBlock* ``)``
       and
       ``pkg_resources.working_set.add_entry(`` *path_to_this_pkg* ``)``


.. _XBlock: https://github.com/edx/XBlock
