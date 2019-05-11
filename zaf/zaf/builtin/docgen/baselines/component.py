expected_rst_output = """
.. _component-comp1(call1):

************
comp1(call1)
************

comp1 description

comp1 extended description

Default scope:
    None

Can:
    can_a, can_b

Priority:
    1

Provided by:
    :ref:`extension-ext1`

Requires
^^^^^^^^

arg:
    component: compA
    , instance: True
    , scope: session
    , can: can_a



Methods
^^^^^^^

.. _method-zaf.application.test.utils.Comp1Class.method:

.. automethod:: zaf.application.test.utils.Comp1Class.method

"""
