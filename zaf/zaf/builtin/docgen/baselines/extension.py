expected_rst_output = """
.. _extension-ext1:

****
Ext1
****

module description.

extended module description

Config Options
==============

ns.<entity>.path
----------------

path description

path extended description

:Cli: --ns-<entity>\\@path
:Type: Path(exists=False)
:Multiple: True

:Commands: :ref:`command-zaf`, :ref:`command-zaf_c2`

Commands
========

:ref:`command-zaf_c1`:
    c1 description

:ref:`command-zaf_c2`:
    c2 description
    c2 description continue

Components
==========

:ref:`component-comp1(call1)`:
    comp1 description



Endpoints
=========

:ref:`endpoint-e1`:
    e1 description

Messages
=========

:ref:`message-m1`:
    m1 description

:ref:`message-m3`:
    m3 description
    continues



Classes
=======

Ext1
----

ext1 description.

ext1 extended description


Related topics
==============

group
-----

* :ref:`extension-ext2`

"""
