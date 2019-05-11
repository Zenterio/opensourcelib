package com.zenterio.jenkins.models

/**
 * The purpose of this test suite is to test the exception mechanism
 * associated with search termination when performing tree searches,
 * with regard to child/children.
 */
class ChildrenSearchExceptionHandlingTest extends GroovyTestCase {

    IModel model

    class Root extends BaseModel {}
    class Level1A extends BaseModel {}
    class Level2A extends BaseModel {}
    class Level3A extends BaseModel {}
    class Level1B extends BaseModel {}
    class Level2B extends BaseModel {}
    class Level3B extends BaseModel {}
    class Last extends BaseModel{}
    class TestException extends Exception {}

     @Override
    void setUp() throws Exception {
        this.model = new Root().with {
            add new Level1A().with {
                add new Level2A().with {
                    add new Level3A()
                }
            }
            add new Level1B().with {
                add new Level2B().with {
                    add new Level3B()
                }
            }
            add new Last()
        }
    }

    /**
     * Any non-search related Exceptions should be triggered
     * as normal.
     */
    void testGetChildrenGeneralExceptionLeaksOut() {

        shouldFail(TestException) {
            this.model.getChildren({ item, result ->
                throw new TestException()
            })
        }
    }

    /**
     * HaltBranchSearchModelException should halt the search
     * in its particular branch, but continue searching in
     * other branches. Since Branch B is not in the results,
     * while Last is, proves this.
     */
    void testGetChildrenHaltBranchShouldIgnoreBranch() {
        List<IModel> result = this.model.getChildren({ item, result ->
            if (item.class == Level1B) {
                throw new HaltBranchSearchModelException()
            }
            true
        })
        // Three from A-branch plus Last
        assert result.size == 4
    }

    /**
     * HaltTreeSearchModelException should halt the search
     * all together but return the current result.
     */
    void testGetChildrenHaltTreeShouldReturnProcessedSoFar() {
        List<IModel> result = this.model.getChildren({ item, result ->
            if (item.class == Level3B) {
                throw new HaltTreeSearchModelException()
            }
            true
        })
        // Three from A-branch plus 1B and 2B.
        // 3B and "Last" will not be included.
        assert result.size == 5
    }

    /**
     * If a search is invalidated, an empty list should be returned.
     */
    void testGetChildrenInvalidateSearchShouldReturnEmptyList() {
        List<IModel> result = this.model.getChildren({ item, result ->
            if (item.class == Last) {
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
    void testGetChildGeneralExceptionLeaksOut() {
        shouldFail(TestException) {
            this.model.getChild({ item, result ->
                throw new TestException()
            })
        }
    }

    /**
     * The filtering makes Level3B the only valid item,
     * but by halting the B branch search, it will never
     * be found.
     */
    void testGetChildHaltBranchShouldIgnoreBranch() {
        IModel result = this.model.getChild({ item, result ->
            if (item.class == Level2B) {
                throw new HaltBranchSearchModelException()
            }
            (item.class == Level3B)
        })
        assert result == null
    }

    /**
     * The filtering makes Level3B the only valid item,
     * but by halting the tree search, it will never
     * be found.
     */
    void testGetChildHaltTreeShouldReturnProcessedSoFar() {
        IModel result = this.model.getChild({ item, result ->
            if (item.class == Level2B) {
                throw new HaltTreeSearchModelException()
            }
            (item.class == Level3B)
        })
        assert result == null
    }

    /**
     * The processing of the last item will cause an invalidation
     * of the whole result, hence return null.
     */
    void testGetChildInvalidateSearchShouldReturnNull() {
        IModel result = this.model.getChild({ item, result ->
            if (item.class == Last) {
                throw new InvalidateTreeSearchModelException()
            }
            false
        })
        assert result == null
    }


}

