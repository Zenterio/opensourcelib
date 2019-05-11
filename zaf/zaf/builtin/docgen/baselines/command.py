expected_rst_output = """
.. _command-zaf_c1:

******
Zaf c1
******

c1 description

c1 extended description


Provided by:
    :ref:`extension-ext1`


Options
=======

bools
-----

bool description

bool extended description

:Cli: --bools
:Type: bool
:Default: (True,)
:Multiple: True



extendable.context
------------------

Included in extendable application context

:Cli: --extendable-context
:Type: str




Extended Options
================

bools
-----

bool description

bool extended description

:Cli: --bools
:Type: bool
:Default: (True,)
:Multiple: True
:Extensions: :ref:`extension-ext2`


ns.entity
---------

entity description

entity extended description

:Cli: --ns-entity
:Type: Entity
:Multiple: True
:Entity: True
:Extensions: :ref:`extension-ext2`

"""
