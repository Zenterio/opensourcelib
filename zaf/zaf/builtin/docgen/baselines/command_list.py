expected_rst_output = """
.. _list-commands:

****************
List of Commands
****************


.. toctree::
    :hidden:
    :glob:

    commands/*


:ref:`command-zaf`:
    The zaf root command.


:ref:`command-zaf_c1`:
    c1 description


:ref:`command-zaf_c2`:
    c2 description
    c2 description continue


:ref:`command-zaf_c2_c3`:
    c3 description
    c3 description continue

"""
