package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty

import groovy.util.GroovyTestCase


class LooseMatchDispatcherTest extends GroovyTestCase  {

    private LooseMatchDispatcher d

    class  TestEntityGenerator implements IEntityGenerator {
        Boolean hasBeenCalled = false
        Object entity

        public TestEntityGenerator(Object entity = null) {
            this.entity = entity
        }

        @Override
        public void generate(ModelEntity model) {
            this.hasBeenCalled = true
            model.entity = this.entity
        }
    }

    class  TestPropertyGenerator implements IPropertyGenerator {
        public Boolean hasBeenCalled = false

        @Override
        public void generate(ModelProperty model, Object entity) {
            this.hasBeenCalled = true
        }
    }

    class SubEntity extends ModelEntity {}

    @Override
    public void setUp() {
        d = new LooseMatchDispatcher();
    }

    public void testMatchesOnExactClass() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(ModelEntity, g)
        assert g.is(d.getGenerator(new ModelEntity()))
    }

    public void testMatchesOnSubClassOfRegistredClass() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(ModelEntity, g)
        assert g.is(d.getGenerator(new SubEntity()))
    }

    public void testGetGeneratorReturnsNullOnNoMatch() {
        assert null == d.getGenerator(new SubEntity())
    }

    public void testDoesNotMatchOnSuperClassOfRegistredClass() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(SubEntity, g)
        assert null == d.getGenerator(new ModelEntity())
    }
}
