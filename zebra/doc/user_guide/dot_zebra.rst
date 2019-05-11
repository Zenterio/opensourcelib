.. _dot_zebra:

**********
Zebra File
**********

A *.zebra* file can be placed in a project to configure the default parameters for zebra.
Currently the only allowed configuration options are image (:ref:`option-image`) and project dir name (:ref:`option-project.dir.name`).
This enables the usage of different default images for different branches or for different directories.

When using a .zebra file the directory with the *.zebra* file will be used as the default project directory (:ref:`option-project.dir`)
and by default the parent of the project will be used as the default root directory (:ref:`option-root.dir`).
This is the same behavior as when standing in the project directory when running zebra.

Format
======

The *.zebra* file is a `YAML <https://en.wikipedia.org/wiki/YAML>`_ file.
The format is very simple and supports only keys and values without a nested structure.

Example ::

    image: abs.u14
    project.dir.name: zids
