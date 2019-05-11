
*********
Profiling
*********

K2 has built in profiling support using `pytracing` and the Chromium trace event profiling tool.

For more information about these tools, please see:

* https://github.com/kwlzn/pytracing
* https://www.chromium.org/developers/how-tos/trace-event-profiling-tool

Note that the profiling tooling generates quite a lot of data and is best suited for short running commands.

How to use
==========

Define the K2_ENABLE_TRACE_PROFILER environment variable and then run K2.
A `trace.out` file will be created in your current working directory.
When running under the profiler, expect K2 to perform significantly slower than normal.

Example usage:

.. code-block:: shell

    K2_ENABLE_TRACE_PROFILER=y zk2 noop

When the `trace.out` file has been created, use your Chrome or Chromium browser and navigate to the `chrome://tracing/` URL.
To begin profiling, load your `trace.out` file.
This may take some time.

Happy profiling!
