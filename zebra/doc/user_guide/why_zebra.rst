
**********
Why Zebra?
**********

Zebra solves the problem that the build environment can be different for all users.
We have two "blessed" Ubuntu releases with different tools and versions of tools.
Even when using these the installation on users computers and on build servers are not always the same.

Solving this problem so that the we control the build environment regardless of
the host installation opens up a lot of possibilities that we currently don't have.
We could even support multiple parallel build environments and select the correct one for the repository, branch
or product.

Less impact of changing/re-installing computer
    With the build environment being handled by Zebra there will be less problem with changing computer.
    Today this can lead to a new version of gcc and other changes that impact the user experience.

Faster adoption of new tools
    By separating the build environment for different branches we could allow for faster adoption
    of new tools on develop without having to test it on every single legacy branch.
    There are a lot of interesting functionality in new gcc and llvm/clang versions that could
    give us speed and quality improvements.

Support for legacy products/branches
    Already today there are some legacy products/branches that require non-supported Ubuntu versions to build
    and when we deprecate Ubuntu 14.04 this will probably turn into an even bigger problem.
    Today users working with support for these product/branches need to have access to computers and build servers
    with these old installations.
    Zebra can completely remove this dependency by providing Ubuntu 12.04 and Ubuntu 14.04 images
    and making it easy to swap between them depending on what is being built.

Sharing of caches
    By having the same build environment on all users computers we can share both mcache and
    `ccache <https://wiki.zenterio.lan/index.php/Ccache>`_ between them.
    By downloading the caches from the latest Jenkins build we could save a lot of compilation time.

A place to add new functionality
    Zebra can provide a common place to add new functionality to combine the
    `build system <https://wiki.zenterio.lan/index.php/Abs>`_ with the rest of the Zenterio tools and services.
    This could for example be a *zebra gdb* command that helps set up gdb and
    helps with finding and downloading the coredump and unstripped rootfs.
