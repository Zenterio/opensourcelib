# Jenkins Seed

Jenkins seed is a tool that takes a set of XML files that defines a build-pipeline
and jobs and generates jenkins configuration using the jobDSL plugin.


## Installation

run the install-script `./install/install` to setup most of what you need.

It will setup the git submodule and create a link in the `./bin` directory
to the version of gradle that comes with the plugin.

Also, install the package moreutils for the tool `parallel`

    sudo apt install moreutils

Also make sure that you have a valid Java JDK for version 8 of the Java APIs.

## Gradle Basics

    ./bin/gradlew tasks - lists all available tasks
    ./bin/gradlew --help


## Updating job-dsl-plugin version

When we change the job-dsl-plugin we need to reflect the new version
in the submodule:

    # cd job-dsl-plugin/
    # git remote add github https://github.com/jenkinsci/job-dsl-plugin.git
    # git fetch github --tags
    # git checkout job-dsl-1.22  (or other version)
    Previous HEAD position was 2d7524b... Releasing 1.21
    HEAD is now at 3c042c2... updated release notes for 1.22
    # cd ..
    # git status
    ...
    #       modified:   job-dsl-plugin (new commits)
    ...
    # git add job-dsl-plugin
    # git commit

Update seed/build.gradle to point to the new version of the jar-file:
def pathJarJobDslCore = 'job-dsl-plugin/job-dsl-core/build/libs/job-dsl-core-1.22.jar'
where the version should match the version in the submodule.

Check that the same version of gradle and junit is used:
build.gradle:

    dependencies {
        compile 'org.codehaus.groovy:groovy-all:1.8.9'
        testCompile 'junit:junit-dep:4.10'
        compile files(pathJarJobDslCore)
    }

The groovy version for the job dsl plugin is set in `job-dsl-plugin/gradle.properties`

    groovyVersion=1.8.9

## Testing

To run all test, invoke the gradle task "check":

    # ./bin/gradlew check --continue

The continue is used to run as much as possible even if some dependency failed.
This to get all error messages at once instead of having to run check multiple
times to find all errors.

To run all unit tests, invoke "test":

    # ./bin/gradlew test

To get the reason for a failed test, add --info flag:

    # ./bin/gradlew test --info

or look in the test report, found in `build/reports/tests/index.html`.

Sometimes the stack-trace is quite complex and it can be hard to find the
zenterio components in the long list. This filtering can help:

    ./bin/gradlew check 3>&1 1>&2 2>&3 3>&- | grep -e "com.zenterio.jenkins"

or set an alias for it:

    alias grcheck='g check 3>&1 1>&2 2>&3 3>&- | grep -e "com.zenterio.jenkins"'

A config file filter can be applied to reduce the config files being parsed.

    ./bin/gradlew check -PconfigFile='<config-file-name> <other-config-file-name>'


A project filter can be applied, to reduce the scope of tasks that reads project
configurations.

    ./bin/gradlew check --continue -PseedProject="Name of project,Name of other project"

Note that when using project filter, the generated content in the build directory
is not deleted, as it is when not using filters.
This to allow small set of changes without getting missing files when diffing with
the baseline. It also has the consequence that files no longer generated will
remain in the build directory until cleaned or config is generated without filters.
Hence, project filters should not be used when generating new baseline for commit,
see below.

After a new reference configuration has been confirmed, replace the existing
baseline in ./test/resources/baseline so the baseline is always up to date.
Some of the testcases generates a configuration and compares it with the current
baseline, so it is important that the stored baseline is correct.
To update the baseline with generated configuration, run gradle task `updateBaseline`

    # ./bin/gradlew updateBaseline

It is important that you have run check with the option --continue not to corrupt
the baseline in the case you have had baseline changes in both the generated
test configuration and production configuration.

### Testing on Staging Server

A set of test configurations is present in `seed/src/test/resources/config/`.
They are designed to test and demo features of jenkins seed.
The generated config can be tested on ci-staging.zenterio.lan

The test config doesn't use the real product repos but instead a repo that
holds a fake build-tool that mimics part of the behavior of ABS. See README
in product-stub repo for more information.

**Workflow:**

1) Make your updates in citools repo (and if needed in relevant stub repositories) and commit.
2) Push stub repositories to origin so that ci-staging can use them.
3) Push citools to branch "staging" using:
  $ git push origin master:staging
  (in case of task-branch replace master with your local branch name).
  It is possible to do forced pushes to the staging branch.
4) Go to: http://ci-staging.zenterio.lan/view/seed/ and run the job
   "seed-test-config".
5) Build the generated projects of interest and test your feature.
6) Verify that the seed-documentation has run, and check the changes you made to documentation.

## Configuration & Data model

The central configuration is done using XML-files located in the config directory.
A test-configuration stored in src/test/resources/testConfig.xml is used
to generate test configuration for testing purposes.

See config/config.dtd for a description of the one-to-many relations

The XML file is parsed into the following data model:

    Project:
        ProjectManager
        TechLead
        Origin:
            Repository:
            Product:
                debug
                    test
                release
                production
                coverity
                documentation

The classes that parses the XML file and the data model are located in
`src/main/groovy/com/zenterio/jenkins/configuration`

See the package info for `com.zenterio.jenkins.configuration` for additional
information about how to write configuration classes.

To print the parsed and resolved configuration, run the gradle task printConfig

    # ./bin/gradlew printConfig

To print the generated model, run the gradle task printModel

    # ./bin/gradlew printModel


Logging
-------
To turn on logging for check task, do

    # gradle check -PlogProfile=<PROFILE>

Profiles:
* quiet
* info
* config
* debug
* all

See also `build.gradle`, and documentation for `com.zenterio.jenkins.logging`

Note! Changing log profile does not necessarily trigger a recompile
and rerun of jenkins configuration. You might need to run
clean in order to notice changes in log profile.


## Coding Guidelines

Follow the style in the context you are working.
If it deviate from the architectural tone,
and it is not much work, consider refactoring to modernize the section.

Groovy have dynamic types but you can still be explicit about the types used.
It makes coding much more efficient since most IDEs can perform code-completion
and refactoring in a safe way.

Groovy is very flexible and offer multiple ways of doing the same thing.
Some guidelines to increase readability and hence reduce the risk for mistakes.

* Use parentheses when calling methods.
  - Exception 1: if you intentionally building a DSL-like structure that
    is isolated to a configuration context.
  - Exception 2: if a closure is the only argument to the method and the
    method doesn't return anything such as list.each {}

OK:

    mylist.each { item -> ... }
    mylist.collect({ item -> ... })

NOK: collect returns a list

    mylist.collect { item -> ... }

* Use explicit variables in Closures, hence avoid the implicit it.
* Use explicit type if known.

BEST:

    projects.each { Project proj ->
     // do something with proj, instance of Project
    }

OK:

    mylist.each { item ->
     // do something with item
    }

NOK:

    mylist.each {
     // do something with it
    }

### Naming convention

constants: ALL_UPPERCASE_UNDERSCORE

classes: UpperCamelCase

methods: lowerCamelCase

variables: lowerCamelCase

enums: EnumClassUperCamelCase, ENUM_VALUE_IS_CONSTANT

    class MyClass {
        public final static MY_CONSTANT = 1

        public void myMethod() {
            int indexForSomething
        }
    }

Use named and typed parameters and return types in method declarations.

OK:

    public void myMethod(String text)

NOK: implicit public Object myMethod(Object text)

    def myMethod(text)

Auto-generate standard utility methods when needed.

    import groovy.transform.AutoClone
    import groovy.transform.Canonical
    import groovy.transform.EqualsAndHashCode

    @AutoClone
    @Canonical
    @EqualsAndHashCode(callSuper=true, includeFields=true)
    class MyClass { ... }

`@AutoClone` creates a value cloning method

`@Canonical` generates equals(), hashCode(), toString()

NOTE! equals only makes use of properties, not fields, by default. Therefore,
we should always add `@EqualsAndHashCode(callSuper=true, includeFields=true)` to
make sure that the generated equal/hashCode match normal expectations.

NOTE! Clone is only a shallow copy, so if deep copy is needed, write your own
custom clone method.

If you have properties that are final, use the following notation, which will
auto-generate a copy-constructor that will be used instead.

    import groovy.transform.AutoClone
    import groovy.transform.AutoCloneStyle

    @AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
    class MyClass {
        final String prop = ""
    }

toString is recursive, meaning, that it will traverse all references to other
objects and append "toString" from them as well. Hence, you cannot have
cyclic dependencies, or you will end up with stack-overflow when it tries
to infinitely print all objects in the cyclic graph.
Use: @Canonical(excludes="propertyName") to exclude properties from being included
in comparison and toString. That is one way of breaking cyclic graphs.

See also resources below for extra options and details:
http://groovy.codehaus.org/api/groovy/transform/AutoClone.html
http://groovy.codehaus.org/gapi/groovy/transform/Canonical.html

### Groovy Properties and Fields

A property is a field with associated getter and setter.
Groovy auto-generates properties if the access modifier is left out.

    class MyClass {
        public String text  // field declaration
        String text2        // property declaration
    }

When accessing a field  using this-variable explicitly, the actual
field is accessed. If just the field name is used, groovy uses the
getters and setters if they are available.

    class MyClass {
        String text // property declaration

        public void foo() {
            this.text = "hello" // access via the field
            print(text)         // access via getText()/property-getter
        }
    }

Use explicit this. whenever possible. This makes it clear that we are accessing
something in the class' local scope. Without this. we might access global values
we are unaware about.

    class MyClass {
        ...
        public void foo() {
            this.bar()            // preferred way
            this.text            // preferred way when accessing fields
            this.getText()        // preferred way when accessing properties
        }
    }

In the scope outside the class, property names get converted to calls to
getter/setter.

    MyClass m = new MyClass()
    m.text        // implicit m.getText()

A good source for reading about properties and fields can be found here:
http://groovy.codehaus.org/Groovy+Beans


Make use of sound Object Oriented principles, such as:
* encapsulation
* use protected member variables primarily and use getters/setters.
* abstractions
* separation of concerns

Follow the SOLID-principles

Use dependency injection via constructor injection to improve testability.

Avoid static members and static methods, it impedes testability.

Short methods, 10-20 LOC
Short files 20-100 LOC


## Documentation

Framework documentation can be generated using the script

    # bin/groovydoc

Some notes on how to write documentation in way that is supported
by the gradle/groovydoc version used in this project:

    /**
     * This is a documentation comment
     */

A documentation comment consists of the following parts.

    /**
     * Summary, the first sentence until first full stop.
     *
     * Description. Can contain multiple sentences and paragraphs.
     *
     * (Only applies to methods)
     * @param variable-name    description of what the variable is used for
     * @return a description of the type, context and value range.
     */

The descriptions should be aligned using spaces if it helps readability.

### Links

Use `{@link }` and fully qualified class path to reference other classes.

    /**
     * {@link com.zenterio.jenkins.models}
     */

Don't use `@see`, doesn't render correct in this version of groovydocs.

Use plain HTML for external links.

    /**
     * <a href="http://www.google.com">Google!</a>
     */

### Paragraphs & Headings

Use `<p>` to separate paragraphs, but not closing `</p>`.

    /**
     * First paragraph
     * <p>
     * Second paragraph
     * <p>
     * Third paragraph
     */

Use `<strong>Title</strong>` for headings.
Don't use `<hN>` tags, they don't render well and disrupts the page flow.

### Code Examples

Use the following to write code examples:

    <code><pre><blockquote>
    </blockquote></pre></code>

You may omit * at the code example section to make indentation of the code
easier to write correctly. The block quote is there to indent the code
and still make it easy to copy paste. White space indentation inside `<pre>` on
base level causes unwanted white-spaces in the copy-paste operation.

    /**
     *
    <pre><code><blockquote>
    Your code goes here!
    </blockquote></code></pre>
     *
     */

Place package wide documentation in package-info.groovy files in the
package directory. Since the entire file is documentation, it is
enough to have leading and trailing documentation markers.

    /**
     *
    Your extensive package documentation
    Spanning many many lines
     *
     */
    package com.zenterio.jenkins.thepackage

However, if you want to include a code example, and in there, include
a package name it must be prefixed with *.

    <code><pre><blockquote>
    *package com.zenterio.jenkins.configuration
    import groovy.transform.AutoClone
    import groovy.transform.Canonical
    import groovy.transform.EqualsAndHashCode

    &#064;AutoClone
    &#064;Canonical
    &#064;EqualsAndHashCode(callSuper=true, includeFields=true)
    class NewConfigClass extends BaseConfig {

       // explicit type (String)
       // implicit property declaration (no visibility modifier)
       String value

       public static getTestData() {
           return new NewConfigClass("Value")
       }
    }
    </blockquote></pre></code>

### Character escaping

Use HTML character escaping for unsafe/special characters such as:

     @  &#064;
     <  &lt;
     >  &gt;
     *  &#42;
     #  &#35;
     $  &#36;

The doc generator run the risk of picking up @text as a document section.
<, > might be interpreted as HTML-tags and rendered as such.
A full list of HTML escaped characters can be found here:
http://www.theukwebdesigncompany.com/articles/entity-escape-characters.php


## Customization of Jenkins

We have done several system wide customizations to jenkins that require special
treatment. Some of those tasks are automated as gradle tasks.

### Custom Job Icons

Run the install/configure-icons script on master to install the custom
icons.

To generate the associated groovy file that is used by the seed application,
run:

    $ ./bin/gradlew generateJobIconFile

This should be done every time the icon files in the icons directory are changed.
The output should be committed as any other source file.


## job-dsl-plugin documentation

https://jenkinsci.github.io/job-dsl-plugin/
