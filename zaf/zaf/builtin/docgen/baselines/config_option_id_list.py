expected_rst_output = """
.. _list-config_option_ids:

**********************
List of Config Options
**********************



.. _option-all.contexts:

all.contexts
============

Included in all application contexts

:Cli: --all-contexts
:Type: str
:Extensions: :ref:`extension-ext3`


.. _option-bools:

bools
=====

bool description

bool extended description

:Cli: --bools
:Type: bool
:Default: (True,)
:Multiple: True
:Extensions: :ref:`extension-ext2`
:Commands: :ref:`command-zaf_c1`

.. _option-extendable.context:

extendable.context
==================

Included in extendable application context

:Cli: --extendable-context
:Type: str
:Extensions: :ref:`extension-ext3`
:Commands: :ref:`command-zaf_c1`

.. _option-ns.<entity>.path:

ns.<entity>.path
================

path description

path extended description

:Cli: --ns-<entity>\\@path
:Type: Path(exists=False)
:Multiple: True
:Extensions: :ref:`extension-ext1`
:Commands: :ref:`command-zaf`, :ref:`command-zaf_c2`

.. _option-ns.entity:

ns.entity
=========

entity description

entity extended description

:Cli: --ns-entity
:Type: Entity
:Multiple: True
:Entity: True
:Extensions: :ref:`extension-ext2`
:Commands: :ref:`command-zaf_c1`, :ref:`command-zaf_c2`
"""
