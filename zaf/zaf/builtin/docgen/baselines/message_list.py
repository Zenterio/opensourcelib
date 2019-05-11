expected_rst_output = """
.. _list-messages:

****************
List of Messages
****************

.. _message-m1:

m1
==

m1 description

m1 extended description


:ref:`endpoint-e1`:
    e1 description


.. _message-m2:

m2
==

m2 description

m2 extended description


:ref:`endpoint-e2`:
    e1 description
    continues


.. _message-m3:

m3
==

m3 description
continues


:ref:`endpoint-e1`:
    e1 description


:ref:`endpoint-e2`:
    e1 description
    continues

"""
