/**
<strong>XML Based Jenkins Seed Configuration</strong>
<p>
The XML based configuration is mainly governed by the
DTD (seed/config/config.dtd).
<p>
<strong>Usage</strong>
<p>
This is a template for normal use:
<code><pre><blockquote>
&lt;project-info name="My Project"&gt;
    &lt;!-- Enable cache for all products --&gt;
    &lt;cache /&gt;

    &lt;!-- Enable coverity for all products, use default stream names (product name) --&gt;
    &lt;coverity /&gt;

    &lt;!-- Enable document generation for all products --&gt;
    &lt;doc /&gt;

    &lt;!-- Enable trigger for all origins, defaults to at midnight --&gt;
    &lt;trigger /&gt;

    &lt;!-- Enable incremental builds for all origins. --&gt;
    &lt;incremental /&gt;

    &lt;!-- Project Manager --&gt;
    &lt;pm name="FIRST LAST" email="first.last@zenterio.com" /&gt;

    &lt;!-- Technical Lead for the project --&gt;
    &lt;techlead name="FIRST LAST" email="first.last@zenterio.com" /&gt;
&lt;/project-info&gt;
&lt;project name="My Project"&gt;
    &lt;origin name="develop"&gt;
        &lt;repository name="zids" dir="zids"
            remote="git@git.zenterio.lan:zids" branch="develop" /&gt;
        &lt;repository name="fs" dir="fs"
            remote="git@git.zenterio.lan:fs" branch="develop" /&gt;
        &lt;product name="ZEN_NAVI_XXXXX"/&gt;
        &lt;product name="ZEN_EKIZ_XXXXX"/&gt;
    &lt;/origin&gt;
&lt;/project&gt;
</blockquote></pre></code>
<p>
<strong>Structure</strong>
<p>
The core <i>structure</i> is:
<code><pre><blockquote>
&lt;project&gt;
    &lt;origin&gt;
        &lt;product&gt;
            &lt;!-- Product Variants (optional) --&gt;
            &lt;debug /&gt;
            &lt;release /&gt;
            &lt;production /&gt;
            &lt;!-- Unit test (optional) --&gt;
            &lt;unit-test /&gt;
        &lt;/product&gt;
    &lt;/origin&gt;
&lt;/project&gt;
</blockquote></pre></code>
<p>
The product-variant elements, <i>debug</i>, <i>release</i> and <i>production</i>,
are implicitly present even if not specified in the configuration.
<p>
The structure element <i>unit-test</i> is implicitly present even if not specified in the configuration.
<p>
<strong>Macro Expansion</strong>
<p>
All string-based attributes and tag values allow for scope context sensitive expansion
of ${PROJECT}, ${ORIGIN}, ${PRODUCT}, ${PRODUCT_ALT_NAME} each expanding to the name of the element.
A lowercase version of each macro also exists, ${project}, ${origin}, ${product}, ${product_alt_name} expanding to the lowercase
version of the name.
<p>
Some tags have custom macro expansions that are unique for their context, such as custom-buildsteps.
That expansion is done post configuration parsing. The mechanism is refered to as scriptlets. See scriptlets for
more information.
<p>
<strong>Properties</strong>
<p>
In addition to the <i>structure</i> tags, the following <i>property</i> tags
are available (applies to different levels of the core structure):
<p>
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead style="background-color: #f0d0d0;">
        <tr>
            <th>Properties</th>
            <th>Project</th>
            <th>Origin</th>
            <th>Product</th>
            <th><i>Product Variants</i></th>
            <th><i>Unit test</i></th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">Build Env</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Build Node</td>
            <td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Build Timeout</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Credential</td>
            <td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Custom Build Step</td>
            <td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Description</td>
            <td>O</td><td>O</td><td>O</td><td>O</td><td>O</td></tr>
        <tr><td style="text-align: left;">Incremental builds</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>-</td></tr>
        <tr><td style="text-align: left;">Log Parsing</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Make Prefix</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Make Root</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Make Target</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O</td></tr>
        <tr><td style="text-align: left;">Project Manager</td>
            <td>R</td><td>O/I</td><td>O/I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Tech Lead</td>
            <td>R</td><td>O/I</td><td>O/I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Resources</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Repository</td>
            <td>-</td><td>R</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Retention Policy</td>
            <td>O</td><td>O/I</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Started By</td>
            <td>O</td><td>O</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Variable</td>
            <td>O&#42;</td><td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td></tr>
        <tr><td style="text-align: left;">Watcher</td>
            <td>O&#42;</td><td>O&#42;/I+</td><td>O&#42;</td><td>O&#42;</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Workspace-browsing</td>
            <td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
    </tbody>
    <tfoot>
    <tr><td colspan="6"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
    <tr><td colspan="6"><i>*=multiple allowed, +=Additive</i></td></tr>
    </tfoot>
</table>
<p>
<strong>Features</strong>
<p>
Features listed as </i>has default</i> "no" is disabled (enabled=false) if the tag is not used in the configuration.
<p>
The following <i>feature</i> tags are available:
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead style="background-color: #d0f0d0;">
        <tr>
            <th>Features</th>
            <th>Has default</th>
            <th>Project</th>
            <th>Origin</th>
            <th>Product</th>
            <th><i>Product Variants</i></th>
            <th><i>Unit Test</i></th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">(Inc) Build-flow</td>
            <td>Y</td><td>O</td><td>O/I</td><td>O/I</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Cache</td>
            <td>N</td><td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Concurrent Builds</td>
            <td>N</td><td>O</td><td>O/I</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Coverity</td>
            <td>N</td><td>O</td><td>O/I</td><td>O/I</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">CSV Data Plot</td>
            <td>N</td><td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Documentation</td>
            <td>N</td><td>O</td><td>O/I</td><td>O/I</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Publish Build Over SSH</td>
            <td>N</td><td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td><td>-</td></tr>
        <tr><td style="text-align: left;">Publish Over SSH</td>
            <td>N</td><td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;/I</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Release Packaging</td>
            <td>Y</td><td>O</td><td>O/I</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">SW upgrade</td>
            <td>N</td><td>O</td><td>O/I</td><td>O/I</td><td>O/I</td><td>-</td></tr>
        <tr><td style="text-align: left;">Trigger</td>
            <td>N</td><td>O</td><td>O/I</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Test Group</td>
            <td>N</td><td>-</td><td>-</td><td>-</td><td>O</td><td>-</td></tr>
    </tbody>
    <tfoot>
    <tr><td colspan="7"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
    <tr><td colspan="7"><i>*=multiple allowed, +=Additive</i></td></tr>
    <tr><td colspan="7"><i>Y=Yes, N=No</i></td></tr>
    </tfoot>
</table>
<p>
<strong>Feature Properties</strong>
<p>
The following <i>property</i> tags are available for the following <i>features</i>.
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead style="background-color: #d0d0f0;">
        <tr>
            <th>Properties</th>
            <th>Coverity</th>
            <th>Documentation</th>
            <th>Release Packaging</th>
            <th>Test Group</th>
            <th>Test Context</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">Build Env</td>
            <td>O/I</td><td>O/I</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Build Nodes</td>
            <td>I</td><td>I</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Build Timeout</td>
            <td>O</td><td>O</td><td>-</td><td>O</td><td>O</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Credential</td>
            <td>O&#42;</td><td>O&#42;</td><td>-</td><td>O&#42;</td><td>O&#42;/I</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Custom Build Step</td>
            <td>O&#42;</td><td>O&#42;</td><td>-</td><td>O&#42;</td><td>O&#42;</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Description</td>
            <td>-</td><td>-</td><td>-</td><td>O</td><td>O</td><td>O</td></tr>
        <tr><td style="text-align: left;">Log Parsing</td>
            <td>I</td><td>I</td><td>-</td><td>O/I</td><td>O</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Make Prefix</td>
            <td>I</td><td>O/I</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Make Root</td>
            <td>I</td><td>O/I</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Make Target</td>
            <td>I</td><td>O</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Project Manager</td>
            <td>I</td><td>I</td><td>-</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Publish Build Over SSH</td>
            <td>-</td><td>O&#42;</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
        <tr><td style="text-align: left;">Publish Over SSH</td>
            <td>O&#42;</td><td>O&#42;</td><td>O&#42;</td><td>O&#42;</td><td>O&#42;</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Publish Test Report Over SSH</td>
            <td>-</td><td>-</td><td>-</td><td>-</td><td>O&#42;</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Tech Lead</td>
            <td>I</td><td>I</td><td>-</td><td>I</td><td>I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Resources</td>
            <td>O</td><td>O</td><td>-</td><td>O</td><td>O</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Repository</td>
            <td>-</td><td>-</td><td>-</td><td>-</td><td>R</td><td>O&#42;!/I</td></tr>
        <tr><td style="text-align: left;">Retention Policy</td>
            <td>I</td><td>I</td><td>-</td><td>-</td><td>O</td><td>O/I</td><td>I</td></tr>
        <tr><td style="text-align: left;">Variable</td>
            <td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td><td>O&#42;/I+</td></tr>
        <tr><td style="text-align: left;">Watcher</td>
            <td>-</td><td>-</td><td>-</td><td>-</td><td>O&#42;</td><td>O&#42;/I+</td></tr>
        <tr><td style="text-align: left;">Workspace browsing</td>
            <td>O</td><td>O</td><td>-</td><td>-</td><td>O</td><td>O/I</td></tr>
    </tbody>
    <tfoot>
    <tr><td colspan="5"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
    <tr><td colspan="5"><i>*=multiple allowed, +=Additive, !=special conditions apply</i></td></tr>
    </tfoot>
</table>
<p>
<strong>Sub properties</strong>
<p>
The following <i>property</i> tag is available to modify property tags.
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead style="background-color: #f0f0d0;">
        <tr>
            <th>Property</th>
            <th>Project Manager</th>
            <th>Tech lead</th>
            <th>Watcher</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">Email policy</td>
            <td>O</td><td>O</td><td>O</td></tr>
    </tbody>
    <tfoot>
    <tr><td colspan="4"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
    <tr><td colspan="4"><i>*=multiple allowed, +=Additive</i></td></tr>
    </tfoot>
</table>

<p>
<strong>Test Properties</strong>
<p>
The following <i>property</i> tags are available for test tags.
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead style="background-color: #d0f0f0;">
        <tr>
            <th>Properties</th>
            <th>Test Group</th>
            <th>Test Context</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">CSV Data Plot</td>
            <td>-</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Duration</td>
            <td>-</td><td>O</td></tr>
        <tr><td style="text-align: left;">EPG</td>
            <td>O&#42;</td><td>O&#42;/I</td></tr>
        <tr><td style="text-align: left;">Image</td>
            <td>O</td><td>O/I</td></tr>
        <tr><td style="text-align: left;">Test Command Args</td>
            <td>-</td><td>O</td></tr>
        <tr><td style="text-align: left;">Test Job Input Parameter</td>
            <td>-</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">Test Suite</td>
            <td>-</td><td>O&#42;</td></tr>
        <tr><td style="text-align: left;">XML to CSV</td>
            <td>-</td><td>O&#42;</td></tr>
    </tbody>
    <tfoot>
    <tr><td colspan="3"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
    <tr><td colspan="3"><i>*=multiple allowed, +=Additive</i></td></tr>
    </tfoot>
</table>
<p>
<strong>Priority and tag-order</strong>
<p>
Some tags can be applied on multiple levels. The most specific tag is the
one in effect. Hence, a feature tag on product level will override the same
tag on origin or project level.
<p>
Product variant configurations can be specified not only on product level
but also on origin and project level. Any new product variant declaration will
supersede previous declarations, independent of the feature or properties specified
inside.
<p>
Product variants will inherit properties and features (as defined by the table
above) from its product configuration except the specific properties and features
explicitly declared inside a product variant.
<p>
What properties and and feature declarations
that will take effect can be a bit tricky to predict.
<p>
Here follows a couple of examples to help clarify the rules:
<code><blockquote>
<strong><i>Property and Feature Declarations</i></strong>
<p>
A property such as a custom build step declared on project level will be
inherited to the origin and further onto the product and its product variants.
<p>
However, general custom build-steps will not apply to coverity builds, they must
be declared explicitly under the coverity tag.
<p>
If any general custom build-steps are declared on a higher level, i.e. origin
or product, that configuration will replace previous configuration, independent
of its mode (override, prepend, append).
<p>
A disabled build-step on higher level will restore build-steps to default.
<p>
<pre>
&lt;project-info name="My Project"&gt;
    &lt;custom-build-step mode="prepend"&gt;A&lt;/custom-build-step&gt;
&lt;/project-info&gt;
&lt;project name="My Project"&gt;
    &lt;origin&gt;
        &lt;custom-build-step mode="append"&gt;B&lt;/custom-build-step&gt;
        &lt;product name="Alpha"&gt;
            &lt;custom-build-step mode"append"&gt;C&lt;/custom-build-step&gt;
       &lt;/product&gt;
       &lt;product name="Beta" /&gt;
       &lt;product name="Omega"&gt;
           &lt;custom-build-step enabled="false" /&gt;
       &lt;/product&gt;
    &lt;/origin&gt;
&lt;/project&gt;
</pre>
<p>
In the example above, custom build-step B will have priority over A.
Product Alpha will have only custom build-step C. Build-steps are not additive. <br/>
Product Beta will have custom build-step B inherited from origin.
Product Omega will have default build-steps due to the disabled custom-build-step
declaration.
</blockquote></code>
<code><blockquote>
<p>
<strong><i>Property and Feature Declarations for Product Variants</i></strong>
<p>
A property such as a description declared in the context of a build variant
e.g. debug, on project level, will affect the description for all debug builds.
<p>
A custom build step declared on project, origin or product level will still
effect the build variant even though it has a custom product variant configuration
for description.
<p>
If a new debug declaration is encountered on a higher level, e.g. product level,
even if it only contains the property watcher or even if its enabled but otherwise
empty will it prevent the description declared for debug on project level to take effect.
<p>
The custom build-step declared outside product-variant contexts will still take effect.
<p>
<pre>
&lt;project-info name="My Project"&gt;
    &lt;custom-build-step&gt;A&lt;/custom-build-step&gt;
&lt;/project-info&gt;
&lt;project name="My Project"&gt;
    &lt;debug&gt;
        &lt;description&gt;D&lt;/description&gt;
    &lt;/debug&gt;
    &lt;origin&gt;
        &lt;product name="Alpha"&gt;
            &lt;debug /&gt;
        &lt;/product&gt;
        &lt;product name="Bravo" /&gt;
    &lt;/origin&gt;
&lt;/project&gt;
</pre>
<p>
In the example above, product Alpha will not have description D for debug builds
due to its empty debug declaration; it will have custom build-step A.<br/>
Product Bravo's debug build will have description D and custom build-step A. <br/>
</blockquote></code>
<p>
The tag order, on a given level, is:
<ol>
<li>Feature tags, alphabetized</li>
<li>Property tags, alphabetized</li>
<li>ProductVariant tags: debug, release, production</li>
<li>Structure tags</li>
</ol>
<p>
<hr>
<p>
<strong>Project</strong>
<p>
The structure tags project-info and project is used to define a project. Several
properties and feature tags can be specified on project level which applies them
to the entire project unless overridden by more specific declarations on origin
or product level.
<code><pre><blockquote>
&lt;project-info name="NAME"/&gt;
&lt;project name="NAME"/&gt;
</blockquote></pre></code>

The structure tag project contains all the origins associated with a project and
project-info contains everything else. Project and project-info tags are
associated by name.

<p>
<strong>Origin</strong>
<p>
The structure tag origin is used to define an origin within a project. A project
can have multiple origins.
An origin provides a code context for the builds, what repositories (and
branches) to build from.
Several properties and feature tags can be specified on origin level which affects
that scope unless overridden by more specific declarations on product level.
<p>
The origin can be made configurable (default "false"), be setting the <i>configurable</i>
attribute to "true". That makes it possible to specify which revision (branch, tag, SHA-1)
to build from, not only the pre-configured value. It shows up as job build parameters
to the origin flow job."
<p>
By default the version used in a clean build is tagged by jenkins. The tag
can be disabled by setting the origin attribute <i>tag-scm</i> to "false".
<code><pre><blockquote>
&lt;origin name="NAME" tag-scm=["true"]|"false" configurable="true"|["false"] /&gt;
</blockquote></pre></code>

<p>
<strong>Product</strong>
<p>
The structure tag product is used to define a product. It reside in the context
of an origin. An origin can contain multiple products. Several properties and features
can be specified on product level.
The product has a name attribute that is used when compiling the product.
An alternative name that is more customer friendly can also be provided. The alternative
name is not widly used but can be accessed using the macro ${PRODUCT_ALT_NAME} and
${product_alt_name} in custom buildstep and similar.
<code><pre><blockquote>
&lt;product name="NAME" alt-name="CUSTOMER FRIENDLY NAME"/&gt;
</blockquote></pre></code>

<p>
<strong>Debug, Release, Production</strong>
<p>
Debug, release and production are product variant tags and can be used to set
custom properties and features specific to each variant. The product variant
tag can be specified on project, origin and product level where higher level
definitions override all product variant specific settings defined on lower level.
<p>
When evaluated, features and properties not specified in a product variant context will
be inherited from its product.
<code><pre><blockquote>
&lt;debug enabled=["true"]|"false"/&gt;
&lt;release enabled=["true"]|"false"/&gt;
&lt;production enabled=["true"]|"false"/&gt;
</blockquote></pre></code>

<p>
<strong>Unit test</strong>
<p>
Unit test is a structure tag, similar to the product variants (see above) and can be used to set
custom properties and features specific to unit test jobs (require built-in="false"). The unit test
tag can be specified on project, origin and product level where higher level
definitions override all unit-test specific settings defined on lower level.
<p>
When evaluated, features and properties not specified in a unit-test context will
be inherited from its product.
<p>
The same settings will be used for both clean and incremental jobs.
<p>
<b>NOTE! if a unit-test is <i>built-in</i>, then the custom settings on the unit test provided by property and feature
tags will not be applicable. They will simply be ignored!.</b>
<p>
<code><pre><blockquote>
&lt;unit-test enabled=["true"]|"false" built-in=["true"]|"false"/&gt;
</blockquote></pre></code>
<p>
<hr>
<p>
<strong>Build Env</strong>
<p>
The Build Env decides which environment that should be used to execute the build.
This can be applied to product-variants, coverity and documentation and will be inherited from project, origin, product.
The current implementation is that Build Env specifies a name of a Docker image that should be used together with the
Zebra tool to set up the environment.
<p>
The env value is the name of a Docker image that is supported by Zebra.
The args can be used to override the arguments to Zebra. If args are not specified the default arguments for the specified
image will be used.
<p>
<code><pre><blockquote>
&lt;build-env env="abs.u16"|["abs.u14"] args="--my-special-argument"/&gt;
</blockquote></pre></code>
<p>

 <strong>Build Node</strong>
<p>
The Build Node applies to a product scope and affects which build-nodes that will perform clean builds
for all builds associated with that product (product-variants, coverity, documentation).
The configuration can be set on project and origin level as well in which case it will apply to all
products in the scope.
<p>
The label value is a jenkins label-expression and the syntax for label expressions can be used for building.
If multiple label tags are specified, they will be or:ed together to form the full
expression.
<p>
If the build-node is not specified, the default build-node is used.
<code><pre><blockquote>
&lt;build-node label="LABEL"|["default"]/&gt;
</blockquote></pre></code>
<p>
<strong>Build Timeout</strong>
<p>
The Build Timeout tag applies to a product variant (including incremental), test context, coverity build, doc build,
unit test build or release packaging,
but it can be set on any level above these as well. It is currently not possible to specify the timeout of flow jobs.
<p>
If left out, a default timeout will be assigned depending on the job type.
<table>
    <tr><td>Compilation</td><td>4h</td></tr>
    <tr><td>Incremental</td><td>4h</td></tr>
    <tr><td>Test</td><td>no timeout</td></tr>
    <tr><td>Coverity</td><td>8h</td></tr>
    <tr><td>Documentation</td><td>1h</td></tr>
    <tr><td>Unit test</td><td>2h</td></tr>
    <tr><td>Release packaging</td><td>1h</td></tr>
</table>
<p>
<code><pre><blockquote>
&lt;build-timeout policy="absolute|disabled|elastic|noactivity" configurable="true|[false]" minutes="[&lt;int&gt;]" fail-build="true|[false]" /&gt;
</blockquote></pre></code>
<p>
    <i>policy</i> and <i>minutes:</i>
<ul>
    <li>absolute: The job is aborted after the number of minutes specified by the minutes attribute. This value must be at least 3.</li>
    <li>disabled: No timeout is specified.</li>
    <li>elastic: The timeout is the calculated as four times the mean from the last three builds. If less then three builds are available, the timeout defaults to the minutes attribute.</li>
    <li>noactivity: The job is aborted after the number of inactive minutes specified in the minutes attribute.</li>
</ul>
<p>
<i>fail-build:</i> If true, the build will be marked as failed insted of aborted, if aborted by a timeout.
<p>
<i>configurable:</i> If true, this will produce an extra parameter by which one can specify the timeout of each build individually.
The default value of this parameter is set by the minutes attribute.
<p>
<p>
<strong>Credential</strong>
<p>
The credential property tag applies to compile jobs but can be set on any level.
Multiple credentials may be given. The tag is optional. The credential tag
provides a means of sharing predefined secrets with a build node.
<p>
<code><pre><blockquote>
&lt;credential type="text|file|username-password" id="identifier" variable-name="variable-name" enabled="true|false"/&gt;
</blockquote></pre></code>
<p>
Credentials are provided to the compile job by binding a secret to a build
variable. If no varible-name is provided, the secret will be bound to a
pre-defined variable name.
<p>
<ul>
    <li>text: The secret is a string stored in CREDENTIAL_TEXT.</li>
    <li>file: The secret is a file. It's path is stored in CREDENTIAL_TEXT</li>
    <li>username-password: The secret is a username/password pair, stored in
    CREDENTIAL_USERNAME and CREDENTIAL_PASSWORD.</li>
</ul>
If a variable-name is provided, the secret will then be stored in a build
variable of that name. If the type is username-password and a variable-name is
provided, the variable-name provided will be postpended with _USERNAME and _PASSWORD.
<p>
Credentials are always considered as a unit. Any credential declaration on a
given level will stop inheriting credentials from the parent. To disable
credential binding on a lower level, provide a credential tag and disable it.
<code><pre><blockquote>
&lt;credential enabled="false"/&gt;
</blockquote></pre></code>
<p>
<b>Note:</b> Users of this tag must handle the secrets with care!
<p>
If the secret is consumed by, for instance, a bash script - be aware that if the
script is run with the <i>set -x</i> option, it is very likely that the secret will
be leaked to the console log. <i>set +x</i>, <i>&#64;echo off</i> or equivalent is
strongly encouraged outside of a debugging setting.
<p>
<strong>Custom Build Step</strong>
<p>
The custom build step property tag applies to product variants but can be set on any level.
Multiple custom build steps can be given. The tag is optional.
Custom build step as a property can also be set on a coverity configuration to
customize the coverity build.
Additionally it can apply to test contexts and will be inherited from the test group.
<p>
Custom build steps are always considered as a unit. Any custom build step declaration
on a given level will stop inheriting the steps from its parent. Hence, to revert
to default build steps on a lower level, set an empty step that is disabled.
<code><pre><blockquote>
&lt;custom-build-step enabled="false"/&gt;
</blockquote></pre></code>
<p>
See also {@link com.zenterio.jenkins.configuration.CustomBuildStep} for available options.
<p>
The repositories declared in origin are available in the executing workspace,
checked out to the appropriate version.
<p>
Artifacts are still picked up from $WORKSPACE/result so artifact files should
be copied there.
<code><pre><blockquote>
&lt;custom-build-step mode="prepend"|"override"|"append"|"override-named" type="shell"|"groovy" enabled="true"|"false" override-name="<name to override>"&gt; script &lt;/custom-build-step&gt;
</blockquote></pre></code>
<p>
See also {@link com.zenterio.jenkins.buildstep.BaseBuildStepScriptlet} for available
macros and example of use.
<p>
<strong>Description</strong>
<p>
The description property tag defines additional information that is shown in association with
the structural element. Description is not inherited but can be set on all
levels.
<code><pre><blockquote>
&lt;description&gt;Description&lt;/description&gt;
</blockquote></pre></code>
<p>
<strong>Incremental builds</strong>
<p>
The incremental property tag indicates that a corresponding
incremental build should be run. Incremental builds poll the source
code every minute to allow very fast feed back on code changes.
<p>
Incremental versions on the origin and product level are created if
there is at least one product variant that should have an incremental
version, ie if there should be an incremental compilation job.
<p>
Incremental jobs are created by default and need to be explicitly disabled
to be omitted from the job generation.
<code><pre><blockquote>
&lt;incremental enabled="true"|"false" /&gt
</blockquote></pre></code>
<p>
<strong>Log Parsing</strong>
<p>
The log parsing tag generates a build step that runs zenterio-zloganalyser
for the console.log. The default is to add log parsing to all applicable jobs
with job type specific config file paths (different for test and compilation).
<code><pre><blockquote>
&lt;log-parsing config="path/to/config.yaml" enabled="true"/&gt;
</blockquote></pre></code>
<p>
<strong>Make Prefix</strong>
<p>
The make prefix tag allows for prefixing the make command to set environmental
variables or prefix with another command. Defaults to <i>empty-string</i> if not set.
<code><pre><blockquote>
&lt;make-prefix value="MAKE_PREFIX" /&gt;
</blockquote></pre></code>
<p>
<strong>Make Root</strong>
<p>
The make root property tag defines what directory, relative to workspace, should be used as root directory for the make command execution. Defaults to <i>zids</i> if not set.
<code><pre><blockquote>
&lt;make-root name="MAKE_ROOT" /&gt;
</blockquote></pre></code>
<p>
<strong>Make Target</strong>
<p>
The make target property tag defines what make target should be built. Defaults to <i>bootimage</i> if not set.
<code><pre><blockquote>
&lt;make-target name="MAKE_TARGET" /&gt;
</blockquote></pre></code>
<p>
<strong>Project Manager</strong>
<p>
The project manager property tag defines contact information to the PM, project manager for the project.
The value is used to render information about the project.
The tag is mandatory on project level, is used on all levels and can be overriden
on lower levels.
<code><pre><blockquote>
&lt;pm name="FIRST LAST" email="first.last@zenterio.com" /&gt;
</blockquote></pre></code>
<p>
<strong>Tech Lead</strong>
<p>
The tech lead property tag defines contact information to the tech lead for the project.
The value is used to render information about the project.
The tag is mandatory on project level, is used on all levels and can be overriden
on lower levels.
<code><pre><blockquote>
&lt;techlead name="FIRST LAST" email="first.last@zenterio.com" /&gt;
</blockquote></pre></code>
<p>
 <strong>Resources</strong>
 <p>
 The Resources can be configured for different types of builds and tests
 (product-variants, incremental product-variants, coverity, documentation, test, release-packaging).
 The configuration can be set on project and origin level as well in which case it will apply to all
 product-variants in the scope. It can also be set on test-group and will be inherited to test-contexts.
 For other types of builds (coverity, documetation, release-packaging) the tag needs to be specified separately.
 <p>
 The functionality uses the Lockable Resources Jenkins plugin and mirrors the concepts of that plugin.
 Either name or label needs to be specified. Name can be a space separated list of multiple specific resources,
 while label can be used to specify a "pool" of resources. Quantity can be used to specify how many of the matching
 resources that should be used. There is no way to request resources for multiple labels by the same build.
 <p>
 Examples of how to combine the different parameters
 <ul>
    <li><em>name="a1 a2" quantity="0"</em>: All requested resources will be used. Build requires both a1 and a2 to run</li>
    <li><em>name="a1 a2" quantity="1"</em>: One of the requested resources will be used. Build requires either a1 and a2 to run</li>
    <li><em>name="a1 a2" quantity="2"</em>: Two of the requested resources will be used. Build requires a1 and a2 to run</li>
    <li><em>label="a" quantity="0"</em>: All resources with the a label are required to run this build. This is probably never good idea</li>
    <li><em>label="a" quantity="1"</em>: One resource with the a label are required to run this build</li>
    <li><em>label="a" quantity="2"</em>: Two resources with the a label are required to run this build</li>
 </ul>
 <p>
 If resources is not specified no extra resources will be used for that Jenkins build.
 <code><pre><blockquote>
 &lt;resources enabled="[true]|false" (name="NAME" label="LABEL) quantity="[0]|QUANTITY"/&gt;
 </blockquote></pre></code>
 <p>
<strong>Repository</strong>
<p>
The repository property tag defines one or more repositories. The tag is mandatory on origin level,
is used on sub-levels but can only be specified on origin level where it affects the build pipeline.
<p>
Repositories are also used in test jobs, where it is mandatory on test-groups but can
be used in test-contexts to override the test-group, IF the test-context has the attribute
upstream set to false.
<code><pre><blockquote>
&lt;repository name="zids" dir="zids"
    remote="git@git.zenterio.lan:zids" branch="develop" /&gt;
</blockquote></pre></code>
<p>
<strong>Retention Policy</strong>
<p>
The retention policy property tag defines how long builds and artifacts should be kept.
The user may choose from five different lengths and can also specify whether to save artifacts or not.
Artifacts are always stored for the last build.
The different choices are:
<ul>
    <li><em>short</em>: last 10 builds are stored.</li>
    <li><em>medium</em>: last 30 builds are stored.</li>
    <li><em>long</em>: last 100 builds are stored.</li>
    <li><em>very-long</em>: last 200 builds are stored.</li>
    <li><em>infinite</em>: No builds are removed.</li>
</ul>
<code><pre><blockquote>
&lt;retention-policy duration="short|medium|long|very-long|infinite" save-artifacts="[true]|false" /&gt;
</blockquote></pre></code>
<p>
<strong>Started By</strong>
<p>
Adds the user ID of the user that triggered the Job or Flow to the Jenkins Build Name.
This is configured on Project or Origin level but is propagated to all Jenkins builds within
the Origin flow.
<code><pre><blockquote>
&lt;started-by enabled="[true]|false" /&gt;
</blockquote></pre></code>
<p>
<strong>Variable</strong>
<p>
Variables are configuration variables that can be declared in a configuration scope and later used
within any string-based attribute or tag value. Multiple variables can be declared.
Declaration of a newly named variable in a sub-scope does not eliminate the effects of
other named variables in a wider scope.
In contrast to many other tags, variables are inherited per tag, not as a group of tags.
Previous declared variables can be changed to have a different value in a sub-scope if declared
again with the same name.
<code><pre><blockquote>
&lt;variable name="var1" value="value1" /&gt;
</blockquote></pre></code>
<p>
Variables can use other variables as part of their value, or macros such as PROJECT, ORIGIN, PRODUCT.
<p>
Hence, if we declare two variables in the project scope where one make use of the other,
the second variable can be re-declared in a sub-scope to also affect the total value
of the first variable when used in that sub-scope.
To access variables in string-attributes, or in other variables, use the macro-token
of the variable name: ${VARIABLE_NAME}.
<code><pre><blockquote>
&lt;variable name="var1" value="some value where only a small part is unique: ${var2}" /&gt;
&lt;variable name="var2" value="scoped-value" /&gt;
</blockquote></pre></code>
If infinite recursive definitions are declared, an exception will be thrown when parsing the configuration.
<code><pre><blockquote>
&lt;variable name="var1" value="${var2}" /&gt;
&lt;variable name="var2" value="${var1}" /&gt;
</blockquote></pre></code>
<p>
<strong>Watcher</strong>
<p>
The watcher property tag defines contact information to people who want to get extra notifications.
Multiple watchers can be specified on any level. Watchers specified on project
level are <i>added</i>to watchers specified on origin level (additive inheritance).
Watchers of origins are not inherited down to its products.
However, watchers can be specified for products and product variants,
and those people will only get notifications for that context.
Watchers of products are not inherited down to product variants.
<code><pre><blockquote>
&lt;watcher name="FIRST LAST" email="first.last@zenterio.com" /&gt;
</blockquote></pre></code>
<p>
<strong>Workspace browsing</strong>
<p>
Workspace browsing is a security property and it defines if the jobs workspace should be able to browse.
It works by overriding the global Project-based Matrix Authorization and re-enabling everything except workspace browsing.
When set enabled = false workspace browsing works only for jenkins-administrators. Setting workspace browsing on a level
will be inherited to all downstream jobs from project down to build variant. test-group is inherited to test-context.
It is possible to override the property by setting (enable = true) at any level to allow a specific jobs workspace to be browsed.

<code><pre><blockquote>
&lt;workspace-browsing enabled="[true]|false" /&gt;
</blockquote></pre></code>
<p>
<strong>Priority</strong>
<p>
The Priority property tag allows you to increase or decrease the priority of jenkins jobs.
It is set at the Origin level and cannot be overridden at any lower level.
Jobs with a higher priority skip ahead of jobs with lower priority in the queue.

<code><pre><blockquote>
&lt;priority level="low|[medium]|high" /&gt;
</blockquote></pre></code>

<p>
<hr>
<p>
<strong>(Inc) Build-flow</strong>
<p>
The build-flow tag is used to define the <i>style</i> of the build-flow to be used. It can be specified on project, origin and
product level. A sibling tag with the same purpose exists for the incremental build flow, <i>inc-build-flow</i>.
<p>
<code><pre><blockquote>
&lt;build-flow style="zids-unit-test-parallel|zids-unit-test-serial|[zids-unit-test-built-in]" /&gt;
&lt;inc-build-flow style="zids-unit-test-parallel|zids-unit-test-serial|[zids-unit-test-built-in]" /&gt;
</blockquote></pre></code>
<p>
<strong>Cache</strong>
<p>
The Cache tag applies to a product variant (including incremental), but it can be set on any level above these as well.
<p>
Cache can also be enabled for unit-test. See feature table for inheritance rules.
<p>
<code><pre><blockquote>
&lt;cache ccache-enabled="[true]|false" ccache-publish="[true]|false" ccache-size="small|[medium]|large" ccache-storage="[${PRODUCT}/${BUILD_TYPE}]" mcache-publish="[true]|false" mcache-enabled="[true]|false" /&gt;
</blockquote></pre></code>
<p>
If Ccache is enabled, A cache will be downloaded from an NFS mount (CCACHE_STORAGE) and
extracted into the specified CCACHE_DIR. Then the call to ABS will be modified to set the
CCACHE_DIR environment variable and to activate ccache by setting ZBLD_CCACHE=y.
As a post build action the cache will be uploaded to the NFS mount again to be used
by other builds on the same or different build servers.
<p>
CcacheStorage relative path, is the path from where the cache-file is fetched.
It defaults to PRODUCT/BUILD_TYPE, but can be specified via the storage attribute,
for e.g release branches that need its own cache-file.
<p>
The configuration of cache is separate between Incremental and normal Compilation
to be able to activate it only for Incremental jobs.
<p>
The maximum size of the ccache directory on disk can be set using the ccache-size attribute.
See {@link com.zenterio.jenkins.configuration.CcacheSize} for the value of the different
sizes. For configurations with publish set to false, the size attribute has no meaning.
For non-publishing jobs an "over-sized" ccache-size will be used to reduce the performance
loss of potential trimming of the ccache that could otherwise occur.
<p>
Mcache works similar to ccache with a step before the build that downloads the mcache files
applicable for the build and a step after the build that publishes them to Artifactory.
<p>
For both types of caches the <cache_type>-publish attribute can be
used to not upload the cache. This is useful for builds that will not be the
base for future development but that could still benefit from using an existing cache.
<p>
<strong>Concurrent Builds</strong>
<p>
The Concurrent Builds tag can be set on an origin and it will make Jenkins allow concurrent builds
for all jobs in the origin that are possible to trigger from the Origin Flow. This does currently not
affect incremental jobs and manually triggered administration jobs like Release Packaging and
Tagging.
<p>
<code><pre><blockquote>
&lt;concurrent-builds enabled="[true]|false" /&gt;
</blockquote></pre></code>
<p>
<strong>Coverity</strong>
<p>
The coverity feature tag applies to a product but can be set on any higher level.
If the stream is not set, it will default to the product name.
If the feature is enabled, a Coverity job will be generated for the products
affected and made part of the build flow. Setting upstream to async disconnects the job from the build flow.
 <p>
Upstream choices:
 <ul>
    <li><em>true</em>: default value, job runs as part of the build flow.</li>
    <li><em>false</em>: not in general build flow or triggered, can be used with periodic to execute at a set time.</li>
    <li><em>async</em>: job gets triggered but is disconnected from the build flow.</li>
 </ul>
 <p>
Aggressiveness attribute enables Coverity to do more aggressive assumptions during the analysis.
Higher levels report more defects, and the analysis time increases.
Values for level are low, medium, or high. Default is low.

<code><pre><blockquote>
&lt;coverity stream="STREAM" upstream="[true]"|"false"|"async" periodic="cron expression" aggressiveness-level="[low]"|"medium"|"high"/&gt;
</blockquote></pre></code>
<p>
<strong>CSV Data Plot</strong>
<p>
The CSV Data Plot applies to product variant but can be set on any higher level.
It can also be applied to test-context but are not inherited from product level.
The tag enables a post build step that makes use of the plot+plugin in jenkins.
<code><pre><blockquote>
&lt;csv-data-plot input="result/data.csv" title="Title" group="Group" scale="Y-axis label" y-min="0" y-max="1" enabled="true"|"false" /&gt;
</blockquote></pre></code>
<p>
<strong>Documentation</strong>
<p>
The doc feature tag applies to a product but can be set on
on any higher level as well.
If the feature is enabled, documentation will be generated for affected
products.
<code><pre><blockquote>
&lt;doc enabled="true"|"false"/&gt;
</blockquote></pre></code>

<p>
<strong>Publish Over SSH and Transfer sets</strong>
<p>
The publish over ssh (POS) feature tag creates a publish over ssh build step.
This build step is appended after custom and ordinary build steps, but before any post build actions or cleanup has been performed.
<p>
Each POS tag represents a connection to a SERVER and each transfer set represents file transfers to and/or command executions on this server.
If a transfer set is configured to do both file transfer and command execution, the file(s) will be transfered before the command is executed.
You can specify as many POS tags in one context as you like and each POS my have any number of transfer sets, but there must always be at least one transfer set in each POS tag.
<p>
The POS tag can be added to projects, origins, products, build-variant, test-groups, test-contexts, doc, coverity and release-packaging tags. <br/>
The inheritance of this tag is as follows <br/>
project >> origin >> product >> build-variants <br/>
test-group >> test-context <br/>
doc <br/>
coverity <br/>
release-packaging <br/>
<p>
<b>Specializations</b><br/>
There exists specializations of the POS, only available for specific contexts that provide preconfigured transfer-sets.
However, these configs are joined with regular POS definitions. A specialization must exist in all contexts affected
by the inheritance chains as described above. So if a specialization can be placed on project level, it will
also need to work for origin, product and build-variants.
<p>
The presens of a specialization tag will block inheritance of other specialization and even the general POS tag.
Same is true for the POS tag, it will prevent specializations from being inherited.
So if a POS tag or any specialization tag exists on in a test-context, it will not inherit the POS or specializations
declared on test-group level.
<code><pre><blockquote>
&lt;publish-over-ssh enabled="[true]|false" server="SERVER" retry-times="[0]" retry-delay-ms="[10000]" label="[]" &gt;
&lt;transfer-set src="[SRC]" remove-prefix="[PREFIX]" remote-dir="[DIR]" exclude-files="[]" pattern-separator="[, ]+"
no-default-excludes="[false]" make-empty-dirs="[false]" flatten-files="[false]" remote-dir-is-date-format="[false]"
exec-timeout-ms="[120000]"exec-in-pseudo-tty="[false]" &gt;
COMMAND
&lt;/transfer-set &gt;
&lt;transfer-set /&gt;
...
&lt;/publish-over-ssh &gt;

&lt;publish-over-ssh &gt;
...
&lt;/publish-over-ssh &gt;

...
</blockquote></pre></code>
<p>
A command will only be executed if a COMMAND is present. <br/>
File transfer(s) will only be executed if the src attribute is present. <br/>
At least one of these options has to be included in each transfer set.

<p>
<strong>Publish Build Over SSH</strong>
<p>
The publish build over SSH (PBOS) feature tag creates a regular publish over ssh action
but with a specific transfer-set to perform the task.
<p>
Each PBOS represents a connection to a SERVER. Multiple tags can be given to publish to multiple servers.
Each PBOS in the same context need to have a unique server - name combination.
<p>
The PBOS will publish the specified artifacts to:<br/>
<pre>/ROOT-DIR/PRODUCT-ALT-NAME/BUILD-TYPE/DATE-ID</pre><br/>
where the DATE-ID has the format:<br/>
<pre>YYYY-MM-DD-build-NN-ext-MM</pre>
where NN and MM are the build-number and the external-build-number of the build.
<p>
If the external build number is missing, no publication will be done. <br/>
<p>
The artifact-pattern attribute is used to specify what artifacts should be published.
The pattern is an ANT file-set pattern.
<p>
The remove-prefix attribute will remove that part of the initial path to the artifacts.
All artifacts copied by the pattern must have the specified prefix. See publish over SSH
transfer-set documentation in the jenkins plugin for details.
<p>
The root-dir attribute is the root directory on the server where the report should
be written to.
<p>
The number of builds to keep attribute specifies how many builds to keep. If there
are more builds publish than the limit, the oldest will be removed.
<p>
The product-alt-name is a customer friendly name for the product and is part
of the publishing directory. If the product-alt-name attribute is not set it
defaults to the products alt-name.
<p>
The PBOS is a specialization of POS. See Publish over SSH for rules of inheritance.
<code><pre><blockquote>
&lt;publish-build-over-ssh enabled="[true]|false" server="SERVER" name="NAME"
 artifact-pattern="ARTIFACT-PATTERN" root-dir="ROOT-DIR" number-of-builds-to-keep="N"
 product-alt-name="[ALT-NAME]"
 retry-times="[0]" retry-delay-ms="[10000]" label="[]" /&gt;
</blockquote></pre></code>

<p>
<strong>Publish Test Report Over SSH</strong>
<p>
The publish test report over SSH (PTROS) feature tag creates a publish over ssh action
but with specific transfer sets to perform the task. See Publish over ssh for more information.
<p>
A matching 'publish-build-over-ssh' with the same name must exist on the compilation job,
otherwise, providing a publish-test-report-over-ssh will result in an error.
<p>
The PTROS is a specialization of POS. See Publish over SSH for rules of inheritance.
<p>
Each PTROS tag represents a connection to a SERVER. Multiple tags can be given to publish to
multiple servers.
<p>
The PTROS requires a matching PBOS<br/>
The PTROS will in turn publish its test reports in the same directory as the build and append
a summary to a specific test result file (not configurable). The summary will contain
data parsed from the test report files (see report-file-pattern).
<p>
The report-file-pattern attribute is a ANT file set for what XML report files that
should be part of the publication.
<p>
The remove-prefix attribute will remove that part of the initial path to the report files.
All files copied by the pattern must have the specified prefix. See publish over SSH
transfer-set documentation in the jenkins plugin for details.
<p>
The suite-name attribute is a customer friendly name for the test suite and should
be unique not to overwrite other test report publications. The suite-name also
affects the filename of the XML test reports.
<code><pre><blockquote>
&lt;publish-test-report-over-ssh enabled="[true]|false" server="SERVER" name="NAME"
 report-file-pattern="REPORT_FILE_PATTERN" suite-name="SUITE"
 retry-times="[0]" retry-delay-ms="[10000]" label="[]" /&gt;
</blockquote></pre></code>

<p>
<strong>Release-packaging</strong>
<p>
The release-packaging feature tag applies to origin but can also be set on project
level.
The release-packaging tag is a container for custom build-steps, publish-over SSH
and log-parsing tags that apply to release packaging jobs.
The release-packaging feature can be disabled, but is on by default.
If the attribute configurable is set to false, the release name will be locked to
the external build number as its version and the tag value to PROJECT_ORIGIN_VERSION.
<p>
<code><pre><blockquote>
&lt;release-packaging configurable="[true]|false" enabled="[true]|false" /&gt;
</blockquote></pre></code>

<p>
<strong>SW upgrade</strong>
<p>
The sw upgrade feature tag applies to a product variant but can be set on
on any level.
This feature will create additional compilations with higher ZSYS_SW_VERSION.
These compilations are done within the compilation build job for a product variant. The offset must be a positive integer.
<p>
It is possible to specify more than one sw upgrade offset and each will create a new set of compilation artifacts with different values for ZSYS_SW_VERSION.
<p>
It is possible to disable the feature by setting enabled="false".
<code><pre><blockquote>
&lt;sw-upgrade offset="offset" enabled="true"|"false"/&gt;
</blockquote></pre></code>
<p>
<strong>Test-group and test-context</strong>
<p>
The test-group feature tag applies to a product variant and is optional. If the
test-group feature is enabled the build result will be tested in the configured
test-context(s).
<p>
The test-group holds information about one specific STB. while the test-context
lists related test suites and when they should be executed.
<p>
Seed supports two types of test tools, Kazam and K2.
The type is specified on the test-group because it affects the interpretation of the test-group attributes.
<p>
Test-group attribute usage depending on <i>type</i>.
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead>
        <tr>
            <th>Attribute</th>
            <th>Kazam</th>
            <th>K2</th>
            <th>Comment</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">box-configuration</td>
            <td>R</td><td>O</td><td>For K2 this is default ${STB_ID} which is used to find the config</td></tr>
        <tr><td style="text-align: left;">product-configuration</td>
            <td>R</td><td>N/A</td><td>-</td></tr>
    </tbody>
    <tfoot>
        <tr><td colspan="4"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
        <tr><td colspan="4"><i>*=multiple allowed, +=Additive</i></td></tr>
    </tfoot>
</table>
<code><pre><blockquote>
...
&lt;debug&gt;
  &lt;test-group name ="groupname" type="kazam|k2" test-root="path" stb-label="jenkins build node name"
      box-configuration="config.cfg" product-configuration="config.cfg" enabled="true"|"false"&gt;
    &lt;description&gt;Description&lt;/description&gt;
    &lt;epg path="CO1000.20160129.579.tar.gz"/&gt;
    &lt;epg path="CO1000.20151219.572.tar.gz"/&gt;
    &lt;image artifact="result/kfs.zmg" enabled="true"|"false" /&gt;
    &lt;repository name="verification" dir="verification"
        remote="git@git.local.zenterio.com:verification" branch="master" /&gt;
    &lt;test-context name = "contextname"
                upstream="true"|"false"|"async"
                polling="&#064;daily"
                periodic="&#064;weekly"
                stb-label="overriding stb-label"
                enabled="true"|"false"&gt;
        &lt;csv-data-plot input="result/data.csv" title="Title" group="Group" scale="Y-axis label" enabled="true"|"false" /&gt;
        &lt;xml-to-csv input="result/data.xml" output="result/data.csv"&gt;
            &lt;xml-data source="data.in.xml" operation="avg" field="data" caption="Caption Avg"/&gt;
            &lt;xml-data source="data.in.xml" operation="min" field="data" caption="Caption Min"/&gt;
            &lt;xml-data source="data.in.xml" operation="max" field="data" caption="Caption Max"/&gt;
        &lt;xml-to-csv/&gt;
        &lt;description&gt;Description&lt;/description&gt;
        &lt;duration time="HH:MM:SS"/&gt;
        &lt;epg .../&gt; -- Override possible
        &lt;image .../&gt; -- Override possible
        &lt;jasmine repository="repo_name" config-file="jasmine_config_file.json" disable-rcu="true"|"false" disable-rcu-check="true"|"false" url="URL/AutoTest.html" /&gt;
        &lt;repository .../&gt; -- Override possible
        &lt;test-report type="junit"/&gt;
        &lt;test-suite path="hugin01/suites/Suite_Stability.xml"/&gt;
        &lt;test-suite path="hugin01/suites/Suite_Menu.xml"/&gt;
        &lt;test-command-args value="--delaystart ${delay}"/&gt;
        &lt;test-job-input-parameter name="delay" default="20"/&gt;
        &lt;watcher name="C Urious" email="curious@example.com"/&gt;
    &lt;/test-context&gt;
    &lt;watcher name="C Urious" email="curious@example.com"/&gt;
  &lt;/test-group&gt;
&lt;/debug&gt;
...
</blockquote></pre></code>
<p>
Test context tag applicability for different test group types.
<table style="text-align: center; border-spacing: 2px 0px;">
    <thead>
        <tr>
            <th>Tag</th>
            <th>Kazam</th>
            <th>K2</th>
            <th>Comment</th>
        </tr>
    </thead>
    <tbody>
        <tr><td style="text-align: left;">csv-data-plot</td>
            <td>O</td><td>N/A</td><td>Not yet compatible with K2</td></tr>
        <tr><td style="text-align: left;">xml-to-csv</td>
            <td>O</td><td>N/A</td><td>K2 will output csv directly</td></tr>
        <tr><td style="text-align: left;">description</td>
            <td>O</td><td>O</td><td>-</td></tr>
        <tr><td style="text-align: left;">jasmine</td>
            <td>O</td><td>N/A</td><td>Not yet compatible with K2</td></tr>
        <tr><td style="text-align: left;">duration</td>
            <td>O</td><td>N/A</td><td>Not yet compatible with K2</td></tr>
        <tr><td style="text-align: left;">epg</td>
            <td>O</td><td>N/A</td><td>-</td></tr>
        <tr><td style="text-align: left;">duration</td>
            <td>O</td><td>N/A</td><td>Not yet compatible with K2</td></tr>
        <tr><td style="text-align: left;">test-report</td>
            <td>O</td><td>O</td><td>-</td></tr>
    </tbody>
    <tfoot>
        <tr><td colspan="4"><i>R=required, O=optional, I=inherited from parent, -=Not applicable</i></td></tr>
        <tr><td colspan="4"><i>*=multiple allowed, +=Additive</i></td></tr>
    </tfoot>
</table>
<p>
The &lt;csv-data-plot&gt; tag can be used to plot data from a csv file e.g. zap-times.
<p>
The &lt;xml-to-csv&gt; tag can be used to invoke the XML2CSV tool to convert data in
an XML-file to CSV format used by the csv-data-plot.
<p>
The &lt;description&gt; tag provides means to add additional information about the test.
<p>
    The &lt;jasmine&gt; tag marks the test context as a Jasmine test. This means that kazam will be launched with some
additional arguments necessary for jasmine tests.<br/>
<ul>
<li>The repository attribute indicates which repository the jasmine tests will be loaded from. This attribute must match the name attribute of one of the repository tags of the test context.</li>
<li>The config-file attribute specifies which jasmine config file to use. </li>
<li>The disable-rcu attribute specifies whether to disable Kazams RCU feature.</li>
<li>The disable-rcu-check attribute specifies whether to disable Kazams RCU connection check.</li>
<li>The url attribute overrides the default jasminebasepage that points at 10.20.10.75/hydra/..</li>
</ul>
<p>
With the the &lt;duration&gt; tag it is possible to set for how long a test suite
will run. When this tag is present, you will get an
argument called "duration" on the test job, with a default value from
the property "time" of the duration tag. The duration value is used by
the test runner script for Kazam to set the loopFor parameter.
<p>
The test-report tag can be used to change the type of test report that
jenkins should look for. The default is the junit type which is the
format that Kazam uses. The testng type will be used for K2 test reports.
<p>
When using multiple epg or test-suite tag, they are used to provide
alternatives when starting the build manually. The default will always
be the first listed epg or test-suite, and those are used when the build
is triggered by polling, periodic or upstream.
<p>
The upstream flag (true/false/async) of a test-context means that a test job
will run automatically whenever the containing product variant is run.
Setting upstream to async disconnects the job from the build flow.
<p>
Polling means that the repositories listed in the test-group or
test-context are polled. This is typically a test resource
repository such as validation, not actual source like zids.
<p>
Periodic means that the build is run at a set time, periodic="" means no active trigger and build will only be manual triggered.
<p>
The stb-label attribute on the test-context can be used to provide an overriding
value at the build-node label for the given context.
The attribute is optional and if not used, the stb-label from the test-group will
be active.
This can be useful to attach additional node conditions such as long running
tests are only allowed to be run on nodes marked as long running
(note the need to escape ampersands in attribute strings):
<code><pre><blockquote>
stb-label="jenkins-node &amp;&amp; long-running"
</blockquote></pre></code>
<p>
Different test-contexts can be used to run different test scenarios in
different situation. e.g. A short smoke test after every build, a larger
feature test every night and a stability testing for seven days once per
week.
<p>
When flashing a box before the test run the artifact (e.g. kfs.zmg) is
always taken from the containing product variant. Which build to pick
is decided as:
<ul>
<li><em>Last successful</em> when triggered by polling or periodic</li>
<li><em>Specific build number</em> when triggered by an upstream build</li>
</ul>
<p>
There are two ways to pass generic data to the running script which can be used together,
as shown in the example above.
<ul>
<li><em>test-command-args</em> is an optional string with additional command arguments to the command run by the test.</li>
<li><em>test-job-input-parameter</em> adds a custom input parameter to the test job in Jenkins.</li>
</ul>
Details on what is possible depends on the individual scriplet.
<p>
<strong>Trigger</strong>
<p>
The trigger feature tag applies to an origin but can also be
set on project level.
If the feature is enabled, the Origin flow jobs will poll the scm and/or run
periodically. It can also be set to react on notifyCommit.
<code><pre><blockquote>
&lt;trigger polling="&#064;midnight" periodic="&#42;/10 &#42; &#42; &#42; &#42;" accept-notify-commit="true"|["false"] enabled="true"|"false"/&gt;
</blockquote></pre></code>
<p>
<strong>Email policy</strong>
<p>
The <i>email-policy</i> tag can be set for pm, tech-lead and watchers to
control when Jenkins sends mail. Note that the policy for sending mails to
developers when the code breaks is not influenced by this mechanism.
<p>
There are four classes of jobs than can send email:
<ul>
<li><i>Fast feedback</i> jobs are currently incremental builds with unit testing.</li>
<li><i>Slow feedback</i> jobs are typically nightly builds with some external testing.</li>
<li><i>Utility</i> jobs are typically manually started tasks such as tagging and promoting build chains.</li>
<li><i>Test</i> jobs are are typically jasmine/kazam test runs, both nightly and incremental.</li>
</ul>
<p>
Email may be send according to one of four policies, indepently for each job class:
<ul>
<li><i>always</i> every time a build finishes.</li>
<li><i>success</i> after each successfull build.</li>
<li><i>failure</i> when the build fails, plus when it first succeeds again.</li>
<li><i>never</i> never</li>
</ul>
<p>
The default corresponds to the following setting:
<code><pre><blockquote>
&lt;email-policy slow-feedback="failure" fast-feedback="never" utility="never"/&gt;
</blockquote></pre></code>
<p>
<hr>
<p>
<strong>Development Notes</strong>
<p>
The class structure should match in terms
of attributes, and allowed hierarchies.
<p>
In general, a class in the configuration package should be matched by a node
in the XML (element in the DTD). A class' properties should be matched by
node attributes.
<p>
Including a tag in the configuration should generally mean that you add
functionality. Hence the default behavior should be that the tag represents
a feature that is enabled. If specific information is required to make
a feature work, that information must be present for enabled features.
Hence, completely empty tags may be allowed, as long as they represent a
valid configuration.
Example:
<code><pre><blockquote>
&lt;!-- valid configuration, enabled --&gt;
&lt;coverity /&gt;

</blockquote></pre></code>
However, this does not mean that the DTD can be made to #REQUIRE data for
all attributes that are required for an enabled feature, since they may be
left out for disabled features.
<p>
By default, features are disabled if the tag are not present. Hence,
a project not having any coverity tag on any level, will not have a
Coverity job in the work-flow.
<p>
<hr>
 *
 */
package com.zenterio.jenkins.configuration.xml
