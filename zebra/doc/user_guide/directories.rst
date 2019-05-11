
.. _directories:

***********
Directories
***********

Zebra maps directories on the host to directories inside the container using Docker mounts.
The directories are calculated using the current working directory (cwd), the directory structure and the following config options.

* :ref:`option-root.dir`
* :ref:`option-container.root.dir`
* :ref:`option-project.dir`
* :ref:`option-project.dir.name`

Defaults
========

By default the *project_dir* is determined by first looking for *.zebra* files in the *cwd* and in parents of the *cwd*
or by looking for other hard coded files that represents the *project_dir* of known projects.
If no such files are found the *project_dir* is set to *cwd*.

The default *root_dir* is the parent directory of the *project_dir*.

The default *container_root_dir* is set to */zebra/workspace*.

.. _project_dir_name:

Project Dir Name
================

If *project_dir_name* is set the name of the *project_dir* will be different inside the container and outside the container.
This can be used to enforce a strict name inside the container while still allowing a different name on the host.

A normal use case for this is that a user might want the same project cloned multiple times to separate directories.
For example cloning your *project* repository as *project1*, *project2* *and project3*.
Specifying *project* as *project_dir_name* will make all of these clones show up as *project* inside the container and functionality that expects
specific paths inside the container will still work.
This is can for example improve caching.

Directory Mapping
=================

The *root_dir* outside the container is mounted as *container_root_dir* and the current working directory inside the container
is set to the relative path between *cwd* and the *root_dir* after applying the *project_dir_name* change.

This means that if the *cwd* is a sub directory to the *project_dir* then the current working directory inside the container
will be the same directory but after mapping the *container_root_dir* and *project_dir_name*.


Examples
========

Example 1 - Defaults
--------------------

root_dir:
    \.\.
project_dir:
    /a/b/c
cwd:
    /a/b/c
container_root_dir:
    /zebra/workspace
project_dir_name:
    None


::

         /a/b                  /c
        root_dir        | project_dir and cwd
    ---------------------------------------------------
     /zebra/workspace          /c
     container_root_dir | project_dir and cwd


Example 2 - Current working directory is sub directory of project_dir
---------------------------------------------------------------------

root_dir:
    \.\.
project_dir:
    /a/b/c
cwd:
    /a/b/c/d/e
container_root_dir:
    /zebra/workspace
project_dir_name:
    None


::

         /a/b                  /c             /d/e
        root_dir         | project_dir  |      cwd
    ---------------------------------------------------
     /zebra/workspace          /c             /d/e
     container_root_dir  | project_dir  |      cwd


Example 3 - Specific root_dir
-----------------------------

root_dir:
    /a
project_dir:
    /a/b/c
cwd:
    /a/b/c/d/e
container_root_dir:
    /zebra/workspace
project_dir_name:
    None


::

         /a                    /b              /c            /d/e
        root_dir         | intermediate   | project_dir |     cwd
    ----------------------------------------------------------------
     /zebra/workspace          /b              /c            /d/e
     container_root_dir  | intermediate   | project_dir |     cwd


Example 3 - container_root_dir
------------------------------

root_dir:
    \.\.
project_dir:
    /a/b/c
cwd:
    /a/b/c/d/e
container_root_dir:
    /something/completely/different
project_dir_name:
    None

::

         /a/b                               /c           /d/e
        root_dir                      | project_dir |     cwd
    --------------------------------------------------------------
     /something/completely/different        /c           /d/e
            container_root_dir        | project_dir |     cwd



Example 4 - project_dir_name
----------------------------

root_dir:
    \.\.
project_dir:
    /a/b/c
cwd:
    /a/b/c/d/e
container_root_dir:
    /zebra/workspace
project_dir_name:
    f


::

         /a/b                     /c            /d/e
        root_dir            | project_dir |      cwd
    --------------------------------------------------
     /zebra/workspace             /f            /d/e
     container_root_dir     | project_dir |      cwd
