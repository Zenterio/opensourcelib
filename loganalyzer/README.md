# LogAnalyzer

Simple tool to analyze logs with the purpose to identify errors or other special
events.

## Usage

Run:

    $ zloganalyzer --help

for available options

## Configuration

The analysis rules are defined by the configuration file passed to the tool
using the first positional argument.

Configuration files can be validated using the following command:

    $ zloganalyzer --config-check-only FILE

Below is an example of the format:

    definitions:
      - title: Title
        id: ID
        desc: Text
        markers:
          - 'reg-ex'
        invalidators:
          - 'reg-ex'
        samples:
          - 'example log line that match marker'
          - 'example log line that match invalidator'

**definitions:**

mandatory, a list of definitions

A definition has the following attributes:
- title
- id
- desc
- markers
- invalidators (optional)
- samples (optional)

**title:**

A string describing the issue in a single sentence style.

**id:**

A short string that can be used for identifying the issue.

**desc:**

A full description of the issue. Can contain multiple lines.

**markers:**

A list of reg-ex:s which identifies the item. The report will list all instances
of completed, all markers matched, found in the log.

**invalidators (optional):**

A list of reg-ex:s which adds rules for when an instance should be discarded as
a false positive. When all the invalidators are matched, the instance is
discarded.

**samples (optional):**

A list of text lines, examples of the log expressions that markers and invalidators
are intended to match against.

##Logging

Logging to file is off by default when running the application, but can be
enabled with the --logfile FILE option.

More verbose logging can be enabled with the --verbose option.

## Development

Run:

    $ znake help

to learn what build options are available.

To setup development environment, run:

    $ znake venv

and follow the instructions.

## Testing

To run unit tests

  $ znake test

To run system tests:

  $ znake systest

To run all tests, run:

  $ znake check

To test a configuration file:

  $ source ./activate
  $ zloganalyzer --config-check-only CONFIG_FILE

## Profiling

To turn on profiling, set environmental variable:

  $ LOG_ANALYZER_PROFILE=True

## Design

General structure of the CLI Application and its components:

    CLI Application
        AnalyzerApplication
            Analyzer
                Trackers
                    ItemDefinitions
                    ItemInstances
                Collector
                Reseters (Not implemented yet)
                    ItemDefinitions
                    ItemInstances
            DataSource
            Reporter

        YAMLConfigParser
        EnvConfigParser
        CommandlineParser

### Analyzer

The analyzer uses trackers to track items in the log. The trackers consists of
item definitions and instances. When an item has full match and is complete, it
is added to the collector. If it becomes invalidated, it is discarded.
Reseters (not implemented yet) is a tracker but with the purpose of identifying
situations when the collected partial results is no longer validated and should
be thrown out - e.g. if the system is being reset/restarted.

#### ItemDefinitions

* markers (currently unordered, but will be made ordered)
* invalidators (currently unordered, but will be made ordered)
* umarkers (not implemented, unordered markers)
* uinvalidators (not implemented, unordered markers)
* title
* id
* description

#### ItemInstance

* each marker         line-nr, text
* each invalidator    line-nr, text
* isInvalid()
* isComplete()

### Data Source

The application fetches data from the data source and feeds it to the analyzer.
A data source could potentially be implemented to read from any data source,
but currently only these are available:

- StreamDataSource
- FileDataSource (uses StreamDataSource)

### Reporter

Takes a collector and generates a report and a summary based on the ItemInstances collected.
Available implementations:

- TextReporter

### Collector

An ordered list of ItemInstances with a defined interface to add items to it and iterate over it.

### Config

* YAML configfile for rule configuration
* Environmental variables to configure debug and profiling
* Commandline to set user options not related to rule configuration


### Analyzer flow and design principles

This section contains a mix of already implemented components and general ideas
for how it aught to work, even perhaps not fully implemented.

In the case of the CLI application, the rule configuration is read via YAMLConfigReader

The config object is independent of the configuration file format and structure.

The AnalyzerApplication is injected with analyzer, reporter and data source.
The analyzer is created by a factory that takes the configuration as an argument.

The application connects the data source and analyzer and drives the data source until it is done.
The data source feeds the analyzer with data.
The analyzer iterates over its trackers and reseters, letting them each parse the data.

The tracker uses the ItemDefinition to create ItemInstances that it keeps track of
until they are complete, at which point they add the instance to the collector and stop tracking it.
If a tracker is reset (not implemented), it throws away any started but incomplete instances.
A tracker can be designed to either keep track of a single instance per definition,
making it overwrite the current instance, or keep track of multiple instances (not implemented).

The reporter is fed the completed items via the collector which it uses to produce its report and summary.

When the data source has no more data, the application completes.

This flow can be designed as a set of generators or it can be done as separate
stages (as in version 0.1).
Ideal would be that each component hooks in to the generator flow and are states
that on termination goes out of scope triggering the cleanup.
That way a reporter could potentially write to file continuously and upon completion,
generate its summary. However, that is of course not possible if the report should be sorted
in any way.

## Planned Improvements

* Have the data source collect stats about itself that can be passed to the reporter
  for better reports.
  - Number of lines, number of data items processed
  - High number of errors also expressed as percentage of processed data
* Named groups in reg-ex:s
  - List top 3 occurrences in the summary for each item
  - List collected attribute: value in report
* Change report to underline matched part instead of printing it on the next line.
* Add configuration option "no-details: true" to not have the item show up in the
  report, but still be part of the summary.
