
.. _docker:

******
Docker
******

Docker is a tool that allows the separation of the host system installation from the target system installation.
This is done using something called containers that uses Linux functionalities like LXC containers, cgroups, namespaces,
etc to provide what looks like a completely separate system but with minimal performance penalties.

Docker also supports the creation of images which makes it possible to distribute complete target system installations
between computers.

Docker Glossary
===============

container:
    A running system that can be interacted with.

image:
    A packaged system that can be distributed between computers and stored in a *registry*.

tag:
    A specific version of an image. (Tags can be used in other ways but this is how they are used by Zebra).

registry:
    A storage of images

pull:
    Fetching an image from a registry
