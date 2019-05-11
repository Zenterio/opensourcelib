
***
FAQ
***

What command-line options are available for zebra?
    Run `zebra --help`.

Something went wrong, how can I troubleshoot Zebra?
    A good first step is to enable more verbose output, using the -v flag.

Should I do a clean build when starting to use Zebra?
    Yes, there could be problems when mixing builds with and without Zebra in the same build directory.
    Zebra by default builds inside the */zebra/workspace* directory.
    This makes all paths for all users exactly the same which is good for caching and other similar functionality.
    The problem is that this results in different absolute paths in the build directory when building with or without Zebra.

Can I run other commands by zebra?
    Yes, :ref:`command-zebra_exec` allows for running any command using Zebra.

Do I need to run "zebra exec gedit/eclipse" to modify files now?
    No, Zebra tries very hard to only be involved in the actual build.
    Everything else can be done on the host computer like before.
    Some tools can benefit from running with *zebra exec* like for example gdb, to get the same environment that was used during the build.

Why zebra complains about files in */zebra/workspace/* but I don't have them on my system?
    Zebra mounts the current working directory (or the zids root directory if it is found) into the */zebra/workspace*
    directory. This is done so that all paths are exactly the same regardless of which host computer the build is done on.

Will zebra work when I am offline or outside the office?
    Yes, If Zebra can't connect to the docker registry it will continue with using the
    latest local version of the build environment.

Can I use Zebra when using a VPN?
    Yes, as long as the default value (host) for the network option (:ref:`option-network`) is used, Zebra should work with VPN.
