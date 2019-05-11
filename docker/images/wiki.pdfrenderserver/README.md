# PDF Render Server for the Mediawiki plugin Collection

## What is this?

In order to generate PDF books with the Mediawiki extension
[Collections][collection-extension], an external PDF render server is
required. This Docker image realizes such a render server.

The Docker image is based on the `python:2-stretch` image, which means it's a
Debian base system.

[collection-extension]: https://www.mediawiki.org/wiki/Extension:Collection

## Patches? Do we need those stinkin' patches?!

Yes, we do. We patch [mwlib][mwlib] and [mwlib.rl][mwlib-rl] to add support for
generating PDFs of pages that contain PlantUML diagrams. We also add Zenterio
copyright text to the page footers.

The patches were generated using `git diff` with no extra parameters, which is
why we use the `-p1` argument when calling `patch`. (Git adds an extra level of
indirection to paths in the diff output.)

The patches apply to specific versions of mwlib and mwlib.rl which is why those
specific versions are checked out after cloning the Git repositories.

[mwlib]: https://github.com/pediapress/mwlib
[mwlib-rl]: https://github.com/pediapress/mwlib.rl

## Suggested volume mounts

The PDF rendering processes use `/cache` as their cache directory (configurable
in `supervisord.conf`), and it would be advisable to mount this as a volume to
stop the Docker container from growing too much.

## Used packages

This chapter outlines the various package dependencies used in this Docker
container.

### Supervisor

The Docker image needs to start four separate processes, and we use
[Supervisor][supervisor] to accomplish this (since it also reaps zombie
processes as expected). The four processes are all configured to log to the
Docker container's stdout and stderr which means `docker logs` works as
expected.

The configuration file used is `supervisord.conf`.

One thing to note is that there is an order to which the processes must start,
which is handled using Supervisor's priority mechanism. (A process with a low
priority number will be started before a process with a higher priority
number).

[supervisor]: http://supervisord.org/

### Java

[PlantUML][plantuml] is distributed as a JAR file so we need Java to be able to
generate PNGs for PlantUML diagrams.

[plantuml]: http://plantuml.com/

### PDF Generation

- pdftk
- imagemagick
- texvc

These are all used when generating the PDFs.

### Other packages

The `re2c` package is used in the build process for the mwlib library.
