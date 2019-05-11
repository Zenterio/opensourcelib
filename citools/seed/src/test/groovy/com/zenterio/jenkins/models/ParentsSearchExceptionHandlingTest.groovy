package com.zenterio.jenkins.models

import groovy.util.GroovyTestCase


/**
 * The purpose of this test suite is to test the exception mechanism
 * associated with search termination when performing tree searches,
 * with regard to parent/parents.
 */
class ParentsSearchExceptionHandlingTest extends GroovyTestCase {

    class Level0 extends BaseModel {}
    class Level1 extends BaseModel {}
    class Level2 extends BaseModel {}
    class Level3 extends BaseModel {}

    class TestException extends Exception {}

    IModel model

     @Override
    void setUp() throws Exception {
        this.model = new Level0()
        new Level3() << new Level2() << new Level1() << this.model
    }

    /**
     * Verify the model structure under test
     */
    void testModelSetup() {
        assert this.model.getParents().size == 3
    }

    /**
     * Any non-search related Exceptions should be triggered
     * as normal.
     */
    void testGetParentsGeneralExceptionLeaksOut() {
        shouldFail(TestException) {
            this.model.getParents({ item, result ->
                throw new TestException()
            })
        }
    }

    /**
     * Since parents is always a chain, the HaltBranchSearchModelException
     * and HaltTreeSearchModelException has the same effect.
     */
    void testGetParentsBothHaltTreeAndHaltBranchShouldHaltSearch() {
        List<IModel> resultBranchHalt = this.model.getParents({ item, result ->
            if (item.class == Level2) {
                throw new HaltBranchSearchModelException()
            }
            true
        })
        assert resultBranchHalt.size == 1

        List<IModel> resultTreeHalt = this.model.getParents({ item, result ->
            if (item.class == Level3) {
                throw new HaltTreeSearchModelException()
            }
            true
        })
        assert resultTreeHalt.size == 2
    }

    void testGetParentsInvalidateSearchShouldReturnEmptyList() {
        List<IModel> result = this.model.getParents({ item, result ->
            if (item.class == Level3) {
                throw new InvalidateTreeSearchModelException()
            }
            true
        })
        assert result.size == 0
    }

    /**
     * Any non-search related Exceptions should be triggered
     * as normal.
     */
    void testGetParentGeneralExceptionLeaksOut() {
        shouldFail(TestException) {
            this.model.getParent({ item, result ->
                throw new TestException()
            })
        }
    }

    /**
     * Since parents is always a chain, the HaltBranchSearchModelException
     * and HaltTreeSearchModelException has the same effect.
     *
     * Due to halting the search on Level2, Level3 will never be reached.
     */
    void testGetParentBothHaltTreeAndHaltBranchShouldHaltSearch() {
        IModel resultBranchHalt = this.model.getParent({ item, result ->
            if (item.class == Level2) {
                throw new HaltBranchSearchModelException()
            }
            (item.class == Level3)
        })
        assert resultBranchHalt == null

        IModel resultTreeHalt = this.model.getParent({ item, result ->
            if (item.class == Level2) {
                throw new HaltTreeSearchModelException()
            }
            (item.class == Level3)
        })
        assert resultTreeHalt == null
    }


    /**
     * The processing of the last item will cause an invalidation
     * of the whole result, hence return null.
     */
    void testGetParentInvalidateSearchShouldReturnNull() {
        IModel result = this.model.getParent({ item, result ->
            if (item.class == Level3) {
                throw new InvalidateTreeSearchModelException()
            }
            false
        })
        assert result == null
    }


}

