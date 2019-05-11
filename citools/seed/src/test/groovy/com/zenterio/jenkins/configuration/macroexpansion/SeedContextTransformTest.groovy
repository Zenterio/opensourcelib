package com.zenterio.jenkins.configuration.macroexpansion

import java.beans.PropertyDescriptor

import com.zenterio.jenkins.configuration.BaseConfig
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.Watcher
import com.zenterio.jenkins.configuration.Variable

class SeedContextTransformTest extends GroovyTestCase {

    ObjectVisitor<BaseConfig> visitor
    ITransform transform
    Project p
    Origin o
    Product prod
    List<BaseConfig> context

    @Override
    protected void setUp() {
        this.transform = new SeedContextTransform()
        this.p = Project.testData
        this.o = Origin.testData
        this.prod = Product.testData
        this.context = [this.p, this.o, this.prod]
    }

    public void testGetConfig() {
        assert this.transform.getConfig(this.context, Project.class) == this.p
        assert this.transform.getConfig(this.context, Origin.class) == this.o
        assert this.transform.getConfig(this.context, Product.class) == this.prod
        assert this.transform.getConfig(this.context, Watcher.class) == null
    }

    public void testTransformStringNormalCase() {
        this.transform.transformString("\${PROJECT}", this.context) == "PROJECT-NAME"
        this.transform.transformString("\${ORIGIN}", this.context) == "ORIGIN-NAME"
        this.transform.transformString("\${PRODUCT}", this.context) == "PRODUCT-NAME"
    }

    public void testTransformStringLowerCase() {
        this.transform.transformString("\${project}", this.context) == "project-name"
        this.transform.transformString("\${origin}", this.context) == "origin-name"
        this.transform.transformString("\${product}", this.context) == "product-name"
    }

    public void testTransform() {
        assert this.transform.transform("\${PROJECT} \${product}", this.context) ==
            "PROJECT-NAME product-name"
        Object o = new Object()
        assert this.transform.transform(o, this.context) == o
        assert this.transform.transform(null, this.context) == null
    }

    public void testVariableContext() {
        /* The function should return the last (most present)
         * variable context (Watcher is not a variable context).
         */
        this.context.add(new Watcher("", "", null))
        assert this.transform.getVariableContext(this.context) == this.prod
    }

    public void testTransformWithVariables() {
        this.prod.variables.clear()
        this.prod.variables.add(new Variable("TEST_VAR1", "test-value1"))
        this.prod.variables.add(new Variable("TEST_VAR2", "test-value2"))
        String input ="\${TEST_VAR1}, \${TEST_VAR2}"
        String expected = "test-value1, test-value2"
        assert this.transform.transform(input, this.context) == expected
    }

    public void testTransformWithIntervariableReference() {
        this.prod.variables.clear()
        this.prod.variables.add(new Variable("TEST_VAR1", "test-\${product}"))
        this.prod.variables.add(new Variable("TEST_VAR2", "TEST_VAR1=\${TEST_VAR1}"))
        String input ="\${TEST_VAR2}"
        String expected = "TEST_VAR1=test-product-name"
        assert this.transform.transform(input, this.context) == expected
    }

    public void testTransformWithRecursiveVariablesThrowsException() {
        this.prod.variables.clear()
        this.prod.variables.add(new Variable("TEST_VAR1", "\${TEST_VAR2}"))
        this.prod.variables.add(new Variable("TEST_VAR2", "\${TEST_VAR1}"))
        String input ="\${TEST_VAR1}"
        shouldFail(RuntimeException) {
            this.transform.transform(input, this.context)
        }
    }

}
