package com.zenterio.jenkins.models

import groovy.util.GroovyTestCase

class BaseModelTestChildHandling extends GroovyTestCase {

    class Super extends BaseModel {}
    class Sub extends Super {}

    BaseModel model

    @Override
    void setUp() throws Exception {
        this.model = new BaseModel()
        // Don't add Super,
        // we want to test non-matches too.
        BaseModel m = new Sub()
        this.model.addChild(m)

        // Second level child, to help verify
        // correct behavior of recursive and non-recursive search
        m.addChild(new Sub())
    }

    /**
     * Strict, non-recursive, search for exact class matches
     */
    void testGetChildrenReturnsPopListForStrictNonRecursiveMatchOnExactClass() {
        assert this.model.getChildren(Sub, true, false).size == 1
    }

    /**
     * Non-Strict, non-recursive, search for exact class matches
     */
    void testGetChildrenReturnsPopListForNonStrictNonRecursiveMatchOnExactClass() {
        assert this.model.getChildren(Sub, false, false).size() == 1
    }

    /**
     * Non-strict, non-recursive, search for super-class matches
     */
    void testGetChildrenReturnsPopListForNonStrictNonRecursiveMatchOnSuperClass() {
        assert this.model.getChildren(Super, false, false).size() == 1
    }

    /**
     * Strict, non-recursive, search for super-class doesn't match on sub-class.
     */
    void testGetChildrenReturnsEmptyListForStrictNonRecursiveNoMatchOnSuperClass() {
        assert this.model.getChildren(Super, true, false).size() == 0
    }

    /**
     * Strict, non-recursive, search for sub-class doesn't match super-class
     */
    void testGetChildrenDontReturnItemOnStrictNonRecursiveForNoMatchOnSubClass() {
        this.model.addChild(new Super()) // Add a super class, not found in search
        // One sub already here on first level.
        assert this.model.getChildren(Sub, true, false).size() == 1
    }

    /**
     * Default behavior
     */
    void testGetChildrenUsesStrictNoneRecursiveOnDefault() {
        assert this.model.getChildren(Super).size() == 0
    }

    /**
     * Strict, non-recursive, search for sub-class doesn't match super class.
     */
    void testGetChildrenDontReturnItemOnStrictForItemSuperClass() {
        this.model.addChild(new Super())
        assert this.model.getChildren(Sub, true, false).size == 1
    }

    /**
     * Strict, recursive, search for sub-class matches all in tree
     */
    void testGetChildrenRecursiveStrictReturnsAllStrictMatchingChildrenInTreeAsList() {
        assert this.model.getChildren(Sub, true, true).size == 2
    }

    /**
     * Non-strict, recursive, search matches all in tree
     */
    void testGetChildrenRecursiveNonStrictReturnsAllLooseMatchingChildrenInTreeAsList() {
        assert this.model.getChildren(Super, false, true).size == 2
    }

    /**
     * Strict, recursive, search for super-class doesn't match sub-class.
     */
    void testGetChildrenRecursiveStrictReturnsEmptyListOnNoMatch() {
        assert this.model.getChildren(Super, true, true).size == 0
    }

    /**
     * Strict, recursive, search for sub-class doesn't match super-class.
     */
    void testGetChildrenRecursiveStrictSubClassNotMatchingSuperClass() {
        this.model.addChild(new Super())
        this.model.children[0].addChild(new Super())
        assert this.model.getChildren(Sub, true, true).size == 2
    }

    /**
     * Closure filtering, blocking all items
     */
    void testGetChildrenRecursiveWithBlockingFilterReturnsEmptyList() {
        assert this.model.getChildren(Super, false, true,
            { item, result -> false }).size == 0
    }

    /**
     * GetChild returns first match. Dept first search
     */
    void testGetChildReturnsFirstMatchDeptFirst() {
        BaseModel item = new Super()
        BaseModel item2 = new Super()
        this.model.addChild(item)
        this.model.children[0].addChild(item2)
        assert this.model.getChild(Super, true, true) == item2
    }

    void testGetChildReturnsFirstMatchUsingLooseMatch() {
        // First item is a subclass of SuperClass
        BaseModel item = this.model.children[0]
        assert this.model.getChild(Super, false) == item
    }

    void testGetChildReturnsFirstMatchRecursiveStrict() {
        BaseModel item = this.model.children[0]
        BaseModel grandChild = new Super()
        item.addChild(grandChild)
        assert this.model.getChild(Super, true, true) == grandChild
    }

    /**
     * Closure filtering, blocking all items
     */
    void testGetChildRecursiveWithBlockingFilterReturnsNull() {
        assert this.model.getChild(Super, false, true,
            { item, result -> false }) ==  null
    }

    /**
     *
     */
    void testGetAtOperatorIsSynonymForGetChild() {
        assert this.model.getChild(Sub) ==
            this.model[Sub]
        assert this.model.getChild(Super) ==
            this.model[Super]
    }

    /**
     * AddChild returns the child
     * Add returns the base
     */
    void testAddReturnDifferentFromAddChild() {
        BaseModel item = new BaseModel()
        BaseModel child = new BaseModel()
        item.add(child)
        assert item.children[0] == child
        assert item.add(child) == item
        assert item.addChild(child) == child
    }

    /**
     * This works since add returns the parent, not the child.
     */
    void testAddInWithBlock() {
        BaseModel item = new BaseModel().with {
            add new BaseModel()
            add new BaseModel()
        }
        assert item.children.size() == 2
    }

    /**
     * Nested with-blocks
     */
    void testAddInNestedWithBlock() {
        BaseModel item = new BaseModel().with {
            add new BaseModel().with {
                add new BaseModel()
            }
        }
        assert item.children.size() == 1
        assert item.children[0].children.size() == 1
    }

    /**
     * Highlight the fact that chaining on add has
     * not the intended effect.
     */
    void testAddChainingHaveDifferentBehaviorToAddChild() {
        BaseModel a = new BaseModel()
        BaseModel b = new BaseModel()
        BaseModel c = new BaseModel()
        a.add(b).add(c)
        assert a.children[0] == b
        assert a.children[1] == c
    }

    /**
     * Highlight that streaming to add-ed items compared to (it), have
     * different results.
     * See Models package documentation for further information.
     */
    void testStreamingToAddedItemHasUnexpectedEffect() {
        BaseModel a = new BaseModel()
        BaseModel b = new BaseModel()
        BaseModel c = new BaseModel()
        BaseModel d = new BaseModel()
        BaseModel e = new BaseModel()
        a.with({
            // this is equal to add (b << c)
            // since b << c returns c, it will
            // be c that is added as child to a.
            // Since a node can only have one connection
            // c is removed from b's child-list when added
            // to a.
            add b << c

            // Expected behavior
            it << d << e
        })

        assert b.children[0] == null
        assert a.children[0] == c
        assert c.parent == a
        assert a.children[1] == d
        assert d.children[0] == e
        assert e.parent == d
    }

    void testNullAreNotAddedToChildren() {
        BaseModel a = new BaseModel()
        a.with {
            add null
            add new BaseModel()
        }
        assert a.children.size() == 1
    }
}

