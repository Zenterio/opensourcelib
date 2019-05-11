package com.zenterio.jenkins.models

import groovy.util.GroovyTestCase


class PropertySelectorTest extends GroovyTestCase {

    class Super extends ModelProperty {};
    class Sub extends Super {};
    class Unique extends Sub {};

    PropertySelector ps
    BaseModel model

    @Override
    void setUp() throws Exception {
        this.model = new BaseModel().with {
            add new Super().with {
                add new Sub()
            }
            add new Sub()

            // The properties of this entity should not come into play
            // as they do not belong to the root model.
            add new ModelEntity().with {
                add new Super()
                add new Sub()
                add new Unique()
            }
        }
        this.ps = new PropertySelector(this.model)

    }

    void testVerifyModel() {
        assert this.model.children.size == 3
        assert this.model.children[0].children.size == 1
        assert this.model.children[1].children.size == 0
        assert this.model.children[2].children.size == 3
        assert this.model.children[2].children[0].children.size == 0
        assert this.model.children[2].children[1].children.size == 0
        assert this.model.children[2].children[2].children.size == 0
    }

    /**
     * Strict, non-recursive, search for exact class matches
     */
    void testGetPropertiesReturnsPopListForStrictNonRecursiveMatch() {
        assert this.ps.getProperties(Sub, true, false).size == 1
        assert this.ps.getProperties(Super, true, false).size == 1
        // not a property
        assert this.ps.getProperties(ModelEntity, true, false).size == 0
    }

    /**
     * Non-Strict, non-recursive, search matches
     */
    void testGetPropertiesReturnsPopListForNonStrictNonRecursiveMatch() {
        assert this.ps.getProperties(Sub, false, false).size() == 1
        assert this.ps.getProperties(Super, false, false).size == 2
        // should hit Super and Sub, since they are of type BaseModel
        // but not the EntityModel since it is not a property
        assert this.ps.getProperties(BaseModel, false, false).size == 2
    }

    /**
     * Default behavior
     */
    void testGetPropertiesUsesStrictNoneRecursiveOnDefault() {
        assert this.ps.getProperties(Super).size == 1
        assert this.ps.getProperties(Sub).size == 1
        assert this.ps.getProperties(BaseModel).size == 0
    }

    /**
     * Strict, recursive, search for sub-class matches all in tree
     */
    void testGetPropertiesRecursiveStrictReturnsAllStrictMatchingChildrenInTreeAsList() {
        assert this.ps.getProperties(Sub, true, true).size == 2
        assert this.ps.getProperties(Super, true, true).size == 1
        assert this.ps.getProperties(BaseModel, true, true).size == 0
    }

    /**
     * Non-strict, recursive, search matches all in tree
     */
    void testGetPropertiesRecursiveNonStrictReturnsAllLooseMatchingChildrenInTreeAsList() {
        assert this.ps.getProperties(Super, false, true).size == 3
        assert this.ps.getProperties(Sub, false, true).size == 2
        assert this.ps.getProperties(BaseModel, false, true).size == 3
    }

    /**
     * Closure filtering, blocking all items
     */
    void testGetPropertiesRecursiveWithBlockingFilterReturnsEmptyList() {
        assert this.ps.getProperties(Super, false, true, { item, result -> false }).size == 0
    }

    /**
     * GetProperty returns first match. Depth first search
     */
    void testGetPropertyReturnsFirstMatchDeptFirst() {
        // strict, recursive
        assert this.ps.getProperty(Sub, true, true) ==
            this.model.children[0].children[0]

        // strict, non-recursive
        assert this.ps.getProperty(Sub, true, false) ==
            this.model.children[1]

        // strict, recursive, out-side scope
        assert this.ps.getProperty(Unique, true, true) == null

        // non-strict, recursive
        assert this.ps.getProperty(Sub, false, true) ==
            this.model.children[0].children[0]
        assert this.ps.getProperty(Super, false, true) ==
            this.model.children[0]

    }

    /**
     * Closure filtering, blocking all items
     */
    void testGetPropertyRecursiveWithBlockingFilterReturnsNull() {
        assert this.ps.getProperty(Super, false, true,
            { item, result -> false }) ==  null
    }

}

