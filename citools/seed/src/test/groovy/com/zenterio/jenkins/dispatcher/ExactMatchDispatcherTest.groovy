package com.zenterio.jenkins.dispatcher

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty


class ExactMatchDispatcherTest extends GroovyTestCase  {

    private ExactMatchDispatcher d

    class TestEntityGenerator implements IEntityGenerator {
        Boolean hasBeenCalled = false
        Object entity
        Boolean throwOnGenerate

        public TestEntityGenerator(Object entity = null, Boolean throwOnGenerate = false) {
            this.entity = entity
            this.throwOnGenerate = throwOnGenerate
        }

        @Override
        public void generate(ModelEntity model) {
            this.hasBeenCalled = true
            model.entity = this.entity
            if (this.throwOnGenerate) {
                throw new HaltDispatchException(model)
            }
        }
    }

    class TestPropertyGenerator implements IPropertyGenerator {
        public Boolean hasBeenCalled = false
        Boolean throwOnGenerate

        public TestPropertyGenerator(Boolean throwOnGenerate=false) {
            this.throwOnGenerate = throwOnGenerate
        }

        @Override
        public void generate(ModelProperty model, Object entity) {
            this.hasBeenCalled = true
            if (this.throwOnGenerate) {
                throw new HaltDispatchException(model)
            }
        }
    }

    class SubEntity extends ModelEntity {}
    class SubProperty extends ModelProperty {}

    @Override
    public void setUp() {
        d = new ExactMatchDispatcher()
    }

    public void testCanRegisterGenerator() {
        d.registerGenerator(ModelEntity, new TestEntityGenerator())
        d.registerGenerator(ModelProperty, new TestPropertyGenerator())
    }

    public void testCanGetGeneratorExactMatch() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(ModelEntity, g)
        assert g.is(d.getGenerator(new ModelEntity()))
    }

    public void testCanDispatchEntityModel() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(ModelEntity, g)
        d.dispatch(new ModelEntity())
        assert true == g.hasBeenCalled
    }

    public void testCanDispatchPropertyModelWithEntityObjPresent() {
        Object entityObj = new Object()
        TestEntityGenerator eg = new TestEntityGenerator(entityObj)
        TestPropertyGenerator pg = new TestPropertyGenerator()
        d.registerGenerator(ModelEntity, eg)
        d.registerGenerator(ModelProperty, pg)
        ModelEntity e = new ModelEntity()
        e.addChild(new ModelProperty())
        d.dispatch(e)
        assert entityObj.is(e.entity)
        assert true == eg.hasBeenCalled
        assert true == pg.hasBeenCalled
    }

    public void testDispatchDoesNotDispatchPropertiesIfEntityObjCanNotBeFound() {
        TestEntityGenerator eg = new TestEntityGenerator(null)
        TestPropertyGenerator pg = new TestPropertyGenerator()
        d.registerGenerator(ModelEntity, eg)
        d.registerGenerator(ModelProperty, pg)
        ModelEntity e = new ModelEntity()
        e.addChild(new ModelProperty())
        d.dispatch(e)
        assert null == e.entity
        assert true == eg.hasBeenCalled
        assert false == pg.hasBeenCalled
    }

    public void testGetGeneratorReturnsNullOnNoMatch() {
        assert null == d.getGenerator(new SubEntity())
    }

    public void testDispatchDoesNotThroughExceptionForModelWithoutGenerator() {
        d.dispatch(new ModelEntity())
    }

    public void testDslLikeRegPossible() {
        TestEntityGenerator eg = new TestEntityGenerator()
        TestPropertyGenerator pg = new TestPropertyGenerator()
        d = new ExactMatchDispatcher().with {
            reg ModelEntity, eg
            reg ModelProperty, pg
        }
        assert eg.is(d.getGenerator(new ModelEntity()))
        assert pg.is(d.getGenerator(new ModelProperty()))
    }

    public void testDoesNotDispatchOnRegisteredSuperClass() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(ModelEntity, g)
        d.dispatch(new SubEntity())
        assert false == g.hasBeenCalled
        d.dispatch(new ModelEntity())
        assert true == g.hasBeenCalled
    }

    public void testDoesNotDispatchOnRegistestedSubClass() {
        TestEntityGenerator g = new TestEntityGenerator()
        d.registerGenerator(SubEntity, g)
        d.dispatch(new ModelEntity())
        assert false == g.hasBeenCalled
        d.dispatch(new SubEntity())
        assert true == g.hasBeenCalled
    }

    public void testDoesNotDispatchChildrenOnHaltDispatchExceptionFromEntityGenerator() {
        TestEntityGenerator egHalt = new TestEntityGenerator(new Object(), true)
        TestEntityGenerator eg = new TestEntityGenerator(new Object(), false)
        TestPropertyGenerator pg = new TestPropertyGenerator(false)
        d = new ExactMatchDispatcher().with {
            reg ModelEntity, egHalt
            reg SubEntity, eg
            reg ModelProperty, pg
        }
        IModel m = new ModelEntity() // This will be generated by egHalt and trigger a HaltDispatchException
        m << new SubEntity()
        m << new ModelProperty()
        d.dispatch(m)
        assert eg.hasBeenCalled == false
        assert pg.hasBeenCalled == false
    }

    public void testDoesNotDispatchChildrenOnHaltDispatchExceptionFromPropertyGenerator() {
        TestEntityGenerator eg = new TestEntityGenerator(new Object(), false)
        TestPropertyGenerator pgHalt = new TestPropertyGenerator(true)
        TestPropertyGenerator pg = new TestPropertyGenerator(false)
        d = new ExactMatchDispatcher().with {
            reg ModelEntity, eg
            reg ModelProperty, pgHalt
            reg SubProperty, pg
        }
        IModel m = new ModelProperty() // This will be generated by pgHalt and trigger a HaltDispatchException
        m << new ModelEntity()
        m << new SubProperty()

        // We need a parent with an entity to properly dispatch the property model.
        new ModelEntity().with {
            entity = new Object()
            add m
        }

        d.dispatch(m)
        assert eg.hasBeenCalled == false
        assert pg.hasBeenCalled == false
    }

    public void testWillDispatchSiblingsToModelOnHaltDispatchExceptionFromEntityGenerator() {
        TestEntityGenerator egHalt = new TestEntityGenerator(new Object(), true)
        TestEntityGenerator eg = new TestEntityGenerator(new Object(), false)
        TestPropertyGenerator pg = new TestPropertyGenerator(false)
        d = new ExactMatchDispatcher().with {
            reg ModelEntity, egHalt
            reg SubEntity, eg
            reg ModelProperty, pg
        }


        IModel m = new SubEntity()
        m << new ModelEntity() // This will be generated by egHalt and trigger a HaltDispatchException
        m << new SubEntity()
        m << new ModelProperty()
        d.dispatch(m)
        assert eg.hasBeenCalled == true
        assert pg.hasBeenCalled == true
    }

    public void testWillDispatchSiblingsToModelOnHaltDispatchExceptionFromPropertyGenerator() {
        TestEntityGenerator eg = new TestEntityGenerator(new Object(), false)
        TestPropertyGenerator pgHalt = new TestPropertyGenerator(true)
        TestPropertyGenerator pg = new TestPropertyGenerator(false)
        d = new ExactMatchDispatcher().with {
            reg ModelEntity, eg
            reg ModelProperty, pgHalt
            reg SubProperty, pg
        }
        ModelEntity m = new ModelEntity()
        m.entity = new Object()
        m << new ModelProperty() // This will be generated by pgHalt and trigger a HaltDispatchException
        m << new SubProperty()
        m << new ModelEntity()

        d.dispatch(m)
        assert eg.hasBeenCalled == true
        assert pg.hasBeenCalled == true
    }
}
