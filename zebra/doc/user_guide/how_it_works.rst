

************
How it works
************

Zebra is a wrapper around Docker commands and provides convenient functionality
for dealing with images, mounts and other :ref:`Docker Concepts <docker>`.

Pull
====

The first thing that happens when running a Zebra command like :ref:`command-zebra_exec` is that
Zebra checks if the wanted image exists on the host computer and that it is up to date.

If the image doesn't exist at all or if there is a newer image available then that image will
be *pulled* from the registry and stored on the host computer.
If for some reason it's not possible to pull the image Zebra will look for it locally and continue
if possible.

Mounts
======

The second thing that Zebra will do is to decide on what should be mounted into the container.
Mounts are used to be able to share files between the host computer and the container.

The following things will be mounted. Some mounts will only be mounted if they exist on the host computer.

${HOME}:
    The users home directory will be mounted into ${HOME} inside the container.
    This is done so that tools that use the home directory for caches and configuration
    will continue to work as expected.

Root directory (default current working directory):
    The root directory will be mounted into /zebra/workspace inside the container by default.
    This is very useful because the same absolute paths will be used regardless of the
    host computer setup.
    The source path can be changed with the :ref:`option-root.dir` option and the target path
    can be changed with the :ref:`option-container.root.dir`.

Project directory:
    An extra mount will be created if :ref:`option-project.dir.name` is used to specify another
    project directory name than the actual directory name.
    This is a way to enforce the exact same directory name inside the docker images regardless of the
    local directory name. For more information see :ref:`project_dir_name`

/etc/group and /etc/passwd:
    These files will be mounted into the container to allow for the same user to be used.
    This solves a lot of problems with permissions, especially of files created inside the container.

/etc/timezone and /etc/localtime:
    These files makes sure that the time inside the container is the same as the time on the host computer.


User
====

Zebra will by default use the same user inside the container that called the command on the host computer.
This simplifies a lot of things that would otherwise cause confusion.

File permissions:
    All files created and modified inside the container will be owned by the user

Access to secrets:
    Some secrets are stored in the home directory of the user that are needed for the build system, or other tools,
    to work correctly.
    This can be things like for example ssh keys.

Persistent data in ${HOME}:
    The container doesn't remember any state between commands so everything that should be kept
    needs to be stored in the host computer file system.
    Example of this is the ccache cache directory that is stored in ~/.ccache.

All this is accomplished by mounting in the user information and home directory into the container
and then run it as the currnent user.
