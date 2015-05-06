Managing Applications using OCCI
--------------------------------

The CC uses a [OCCI]_ based API/Interface for interactions. The following
passages therefore describe how to interact with the CC.

The OCCI PaaS model
===================

An application in the PaaS space is defined in this OCCI rendering with the
following Category::

  Category: app; scheme="http://schemas.ogf.org/occi/platform#"

This category has the following attributes defined:

==============  ==============================  ==========
Attribute       Description                     Mutability
==============  ==============================  ==========
occi.app.repo   Repository of the source code.  immutable
occi.app.name   DNS name of the application.    required
occi.app.url    DNS entry of the application.   immutable
occi.app.state  Status of the application.      immutable
==============  ==============================  ==========

An application in general can be in 3 states:

* Active: Application is running.
* Inactive: Application is being upgraded, maintained etc.
* Error: Application is in a error state

Transitions between the states can be triggered using actions. To describe
the *type* and *size* of deployment of the application Resource and
Application templates are available::

    res_tpl; scheme="http://schemas.ogf.org/occi/platform#"
    app_tpl; scheme="http://schemas.ogf.org/occi/platform#"

Handling Applications
=====================

Querying capabilities
^^^^^^^^^^^^^^^^^^^^^

To figure out what kind of application can be deployed and what capabilities
are available the QI can be used. A simple GET operation will return the
Category definitions::

    curl -X GET http(s)://<host:port>/-/

Creating an application
^^^^^^^^^^^^^^^^^^^^^^^

From the previous step a resource and application template can be selected
and provided next to the required attributes - as the following example show:

* Application template (which relates to the scheme described above): python-2.7;scheme="http://schemas.openshift.com/template/app#"
* Resource template  (which relates to the scheme described above): medium;scheme="http://schemas.openshift.com/template/app#"
* Attribute: occi.app.name="test"

This information can be posted to the service (you can figure out the url
from the QI)::

    curl -X POST http(s)://<host:port>/app/ \
      -H 'Category: app; scheme="http://schemas.ogf.org/occi/platform#"' \
      -H 'Category: python-2.7; scheme="http://schemas.openshift.com/template/app#"' \
      -H 'Category: medium; scheme="http://schemas.openshift.com/template/app#"' \
      -H 'X-OCCI-Attribute: occi.app.name=test'

The service will return a URI of the new application which then can be
retrieved.

Triggering actions
^^^^^^^^^^^^^^^^^^

Actions for state transitions can be triggered as follows (the correct link
can be retrieved from the application description)::

    curl -X POST http(s)://<host:port>/app/<uid>?action=stop \
      -H 'Category: stop; scheme="http://schemas.ogf.org/occi/platform/app/action#"'

OpenShift specifics
===================

N/A

References
==========

..  [OCCI] http://www.occi-wg.org