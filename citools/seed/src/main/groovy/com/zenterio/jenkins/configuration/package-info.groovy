/**
 *
<strong>Seed Configuration Classes</strong>
<p>
The configuration classes defined the configuration data set available in the
application, a definition independent of how it is generated.
<p>
Configuration file parsers should produce a data tree using instances of these
classes.
<p>
<strong>Conventions</strong>
<p>
With very few exceptions, all configuration classes should follow the same
basic layout:
<ul>
<li>use implicit property declaration with explicit types</li>
<li>always inherit from BaseConfig or one of its sub-classes</li>
<li>use Canonical in conjunction, EqualsAndHashCode, AutoClone</li>
<li>supply a public static testData method that returns a configured instance</li>
</ul>
<p>
<p>
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

<p>
<strong>Test</strong>
<p>
Testing is mandatory
<ul>
<li>all classes should have corresponding unit test file</li>
<li>must have test to ensure that they handle equals and clone correctly</li>
<li>all helper methods with logic should have a matching test</li>
</ul>
<p>
<code><pre><blockquote>
*package com.zenterio.jenkins.configuration

class NewConfigClassTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        NewConfigClass cfg = NewConfigClass.testData
        NewConfigClass clone = cfg.clone()
        assert cfg == clone
        assert !cfg.is(clone)
    }

    public void testAdvancedMethod() {...}
}
</blockquote></pre></code>


 *
 */
package com.zenterio.jenkins.configuration
