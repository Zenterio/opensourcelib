package com.zenterio.jenkins.models

import groovy.util.GroovyTestCase


class PropertySelectorParentPropertiesTest extends GroovyTestCase {

    class Super extends ModelProperty {};
    class Sub extends Super {};
    class Unique extends Sub {};

    ModelEntity root

    @Override
    void setUp() throws Exception {
        this.root = new ModelEntity().with {
            add new Super()
            add new Unique().with {
                add new Sub()
            }
            add new ModelEntity().with {
                add new Super()
                add new Sub().with {
                    add new Unique()
                }
            }
        }
    }

    void testVerifyModel() {
        this.root.children.size == 3
        this.root.children[0].children.size == 0
        this.root.children[1].children.size == 1
        this.root.children[1].children[0].children.size == 0
        this.root.children[2].children.size == 2
        this.root.children[2].children[0].children.size == 0
        this.root.children[2].children[1].children.size == 1
        this.root.children[2].children[1].children[0].children.size == 0
    }

    /**
     * Get parent property using defaults (strict, non-recursive)
     */
    void testGetParentPropertyReturnsModelOnMatchUsingDefaults() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperty(Unique) == this.root.children[1]
    }

    /**
     * Get parent property using strict and recursive
     */
    void testGetParentPropertyReturnsModelOnMatchStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperty(Sub, true, true) == this.root.children[1].children[0]
    }

    /**
     * Get parent property using non-strict and recursive
     */
    void testGetParentPropertyReturnsModelOnMatchNonStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperty(Sub, false, true) == this.root.children[1]
    }

    /**
     * Get parent properties using defaults (strict, non-recursive)
     */
    void testGetParentPropertiesReturnsListOnMatchUsingDefaults() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperties(Unique).size == 1
    }

    /**
     * Get parent properties using strict and recursive
     */
    void testGetParentPropertiesReturnsListOnMatchStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperties(Sub, true, true).size == 1
    }

    /**
     * Get parent properties using non-strict and recursive
     */
    void testGetParentPropertiesReturnsListOnMatchNonStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2]
        assert ps.getParentProperties(Sub, false, true).size == 2
    }

    /**
     * Get parents with property using defaults (strict, non-recursive)
     */
    void testGetParentsWithPropertyReturnsModelOnMatchUsingDefaults() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2].children[0]
        assert ps.getParentsWithProperty(Unique).size == 1
    }

    /**
     * Get parents with property using strict and recursive
     */
    void testGetParentsWithPropertyReturnsModelOnMatchStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2].children[0]
        assert ps.getParentsWithProperty(Sub, true, true).size == 2
    }

    /**
     * Get parents with property using non-strict and recursive
     */
    void testGetParentsWithPropertyReturnsModelOnMatchNonStrictRecursive() {
        IPropertySelector ps = (IPropertySelector)this.root.children[2].children[0]
        assert ps.getParentsWithProperty(Sub, false, true).size == 2
    }

}

