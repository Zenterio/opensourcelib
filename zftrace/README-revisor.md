#Revisor#

###Description###
Revisor is a strace-based audit tool intended to be used for build audit
and version control agnostic build avoidance implementation.

Idea is to trace all files used for a build and then prepare a report that
will consist of a list of files and checksums for them. Files generated
during the build will be not included because we don't have interest in them.

###License###
Revisor is just a fork of [strace](http://sourceforge.net/projects/strace) and
use the same license
([New BSD License](http://en.wikipedia.org/wiki/BSD_licenses))
as original project.

###Features###
- Absolute paths extracted for all files included into the report
- Environment variables support. Part of path's could be replaced
  by environment variables name to remove absolute path's to tracked files
- Conditional triggering for continuous integration builds, i.e.
  conditional execution based on provided revisor report.
  Revisor will parse provided report and execute command only if
  any file was changed
- Possibility to ignore patterns to exclude files from /app, /dev and other
  system directories

###Usage examples###
- Build (or any other) process tracking
<pre>
$ revisor -o revisor.report make
/bin/mkdir -p ./linux
cat ./linux/ioctlent.h.in ./linux/x86_64/ioctlent.h.in | \
........
mv -f .deps/ftrace.Tpo .deps/ftrace.Po
gcc -Wall -Wwrite-strings -g -O2 -lmhash -lglib-2.0  -o revisor strace.o ...
make[2]: Leaving directory '/home/USER/revisor'
make[1]: Leaving directory '/home/USER/revisor'
$ less revisor.log
eb52cecb4dde74e6e95dd0bebed40887        /bin/bash
6b35e2f5d929ccb488b035d4e9712169        /bin/cat
1407e3f1c1fc951a11607c26ff5ba36d        /bin/mkdir
89d5a86f3ed73eaeadface4413bd0a66        /bin/mv
47b35a67b6d5c2685cbecb7a2efe5c63        /bin/rm
057c0ee34908d740e661732b82079b20        /bin/sed
371cf9a78bd16e8abef50ab006218fe1        /bin/sort
d41d8cd98f00b204e9800998ecf8427e        /dev/tty
03ebe95773fb8c5c240edf22b32171b4        /etc/ld.so.cache
d631bcfb15cfca85da064e5b5f074398        /etc/ld.so.conf
f16e1a8436b3039dd5e3a0ffff610de5        /etc/ld.so.conf.d/CASA.conf
632083d65de8c2598d1b3f44e242f97f        /etc/ld.so.conf.d/ghostscript-omni.conf
9dd391ccf615cdc055397b3be43ad7f3        /etc/ld.so.conf.d/graphviz.conf
cbeb085a2f90ada12ed999857782d91b        /etc/ld.so.conf.d/novell-NLDAPsdk-dyn.conf
e3e9532b720d4ef699ab7c1236d8bddf        /etc/ld.so.conf.d/samba4.conf
612f0761d4f540709d127c9945cf0be3        /home/USER/revisor/bjm.c
e87f435e68a2368b38281ffe48397039        /home/USER/revisor/block.c
421ff7f7e12cc337faf83bf16684e619        /home/USER/revisor/config.h
92517dd7759bc96d8183ab4162835171        /home/USER/revisor/count.c
c47db23b1172a506bd120b03db80a65f        /home/USER/revisor/defs.h
1f73967d2002c09531ca0f546daf4f91        /home/USER/revisor/desc.c
a266a9e51ca522f589119f1263b4775c        /home/USER/revisor/file.c
095973066b93ebf7954da67a48efdc73        /home/USER/revisor/ftrace.c
d66e1f95f36ba29d83101ca8774f432f        /home/USER/revisor/io.c
0fd0c1a9c4932b611f992f413cabbce9        /home/USER/revisor/ioctl.c
c905a113f0d1a1067c7fd8ba0d7d2e30        /home/USER/revisor/ipc.c
........
</pre>

- Build (or any other) process tracking + ignore rules
<pre>
$ cat revisorignore
^/bin/.*
^/etc/.*
$ revisor -o revisor.report -i revisorignor make
/bin/mkdir -p ./linux
cat ./linux/ioctlent.h.in ./linux/x86_64/ioctlent.h.in | \
........
mv -f .deps/ftrace.Tpo .deps/ftrace.Po
gcc -Wall -Wwrite-strings -g -O2 -lmhash -lglib-2.0  -o revisor strace.o ...
make[2]: Leaving directory '/home/USER/revisor'
make[1]: Leaving directory '/home/USER/revisor'
$ less revisor.log
612f0761d4f540709d127c9945cf0be3        /home/USER/revisor/bjm.c
e87f435e68a2368b38281ffe48397039        /home/USER/revisor/block.c
421ff7f7e12cc337faf83bf16684e619        /home/USER/revisor/config.h
92517dd7759bc96d8183ab4162835171        /home/USER/revisor/count.c
c47db23b1172a506bd120b03db80a65f        /home/USER/revisor/defs.h
1f73967d2002c09531ca0f546daf4f91        /home/USER/revisor/desc.c
a266a9e51ca522f589119f1263b4775c        /home/USER/revisor/file.c
095973066b93ebf7954da67a48efdc73        /home/USER/revisor/ftrace.c
d66e1f95f36ba29d83101ca8774f432f        /home/USER/revisor/io.c
0fd0c1a9c4932b611f992f413cabbce9        /home/USER/revisor/ioctl.c
c905a113f0d1a1067c7fd8ba0d7d2e30        /home/USER/revisor/ipc.c
........
</pre>

- Build (or any other) process tracking + ignore rules + environment variables
<pre>
$ cat revisorignore
^/bin/.*
^/etc/.*
$echo $REPOSITORY
/home/USER/revisor
$ revisor -o revisor.report -i revisorignor -s REPOSITORY make
/bin/mkdir -p ./linux
cat ./linux/ioctlent.h.in ./linux/x86_64/ioctlent.h.in | \
........
mv -f .deps/ftrace.Tpo .deps/ftrace.Po
gcc -Wall -Wwrite-strings -g -O2 -lmhash -lglib-2.0  -o revisor strace.o ...
make[2]: Leaving directory '/home/USER/revisor'
make[1]: Leaving directory '/home/USER/revisor'
$ less revisor.log
612f0761d4f540709d127c9945cf0be3        $REPOSITORY/bjm.c
e87f435e68a2368b38281ffe48397039        $REPOSITORY/block.c
421ff7f7e12cc337faf83bf16684e619        $REPOSITORY/config.h
92517dd7759bc96d8183ab4162835171        $REPOSITORY/count.c
c47db23b1172a506bd120b03db80a65f        $REPOSITORY/defs.h
1f73967d2002c09531ca0f546daf4f91        $REPOSITORY/desc.c
a266a9e51ca522f589119f1263b4775c        $REPOSITORY/file.c
095973066b93ebf7954da67a48efdc73        $REPOSITORY/ftrace.c
d66e1f95f36ba29d83101ca8774f432f        $REPOSITORY/io.c
0fd0c1a9c4932b611f992f413cabbce9        $REPOSITORY/ioctl.c
c905a113f0d1a1067c7fd8ba0d7d2e30        $REPOSITORY/ipc.c
........
</pre>

- Build (or any other) process tracking + ignore rules + environment
variables + conditional trigger
<pre>
$ cat revisorignore
^/bin/.*
^/etc/.*
$ cat revisor.log
612f0761d4f540709d127c9945cf0be3        $REPOSITORY/bjm.c
e87f435e68a2368b38281ffe48397039        $REPOSITORY/block.c
421ff7f7e12cc337faf83bf16684e619        $REPOSITORY/config.h
92517dd7759bc96d8183ab4162835171        $REPOSITORY/count.c
c47db23b1172a506bd120b03db80a65f        $REPOSITORY/defs.h
1f73967d2002c09531ca0f546daf4f91        $REPOSITORY/desc.c
a266a9e51ca522f589119f1263b4775c        $REPOSITORY/file.c
095973066b93ebf7954da67a48efdc73        $REPOSITORY/ftrace.c
d66e1f95f36ba29d83101ca8774f432f        $REPOSITORY/io.c
0fd0c1a9c4932b611f992f413cabbce9        $REPOSITORY/ioctl.c
c905a113f0d1a1067c7fd8ba0d7d2e30        $REPOSITORY/ipc.c
........
$ revisor -o revisor.report -c revisor.report -i revisorignor -s REPOSITORY make
No changes found. Skip command execution
</pre>

- Look up for changes using revisor report
<pre>
$ revisor -o revisor.report -i revisorignor make
...
$ echo "Do modifications for io.c" >> /home/USER/revisor/io.c
$ revisor -l revisor.report
Changes found for /home/USER/revisor/io.c
</pre>
