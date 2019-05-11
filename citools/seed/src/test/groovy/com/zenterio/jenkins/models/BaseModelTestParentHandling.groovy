package com.zenterio.jenkins.models

class BaseModelTestParentHandling extends GroovyTestCase {

    class Super extends BaseModel {}
    class Sub extends Super {}

    BaseModel model
    BaseModel superCls
    BaseModel subCls

    @Override
    void setUp() throws Exception {
        this.model = new BaseModel()
        this.superCls = new Super()
        this.subCls = new Sub()
        this.model.parent = this.subCls
        this.model.parent.parent = this.superCls
    }

    void testUnsetParentReturnsNullIfParentIsNotSet() {
        assert null == new BaseModel().unsetParent()
    }

    void testUnsetParenHasNoEffectAndReturnsNullIfProvidedParentDoesNotMatch() {
        assert null == this.model.unsetParent(new BaseModel())
        assert this.model.parent != null
    }

    void testUnsetParentSetsParentToNull() {
        this.model.unsetParent()
        assert null == this.model.parent
    }

    void testUnsetParentSetsParentToNUllIfProvidedParentMatch() {
        assert this.subCls == this.model.unsetParent(this.subCls)
        assert null == this.model.parent
    }

    void testGetParentWithClassUsesStrictMatchByDefault() {
        assert this.model.getParent(Super) == this.superCls
        assert this.model.getParent(Sub) == this.subCls
    }

    void testGetParentWithClassWorksWithLooseMatch() {
        assert this.model.getParent(Super, false) == this.subCls
    }

    void testGetParentWithNoMatchReturnsNull() {
        assert this.model.getParent(BaseModel, true) == null
    }

    void testGetParentsWithNoParentReturnsEmptyList() {
        assert (new BaseModel()).getParents().size == 0
    }

    void testGetParentsWithClassUsesStrictMatchByDefault() {
        assert this.model.getParents(Sub) == [this.subCls] as List<IModel>
        assert this.model.getParents(Super) == [this.superCls] as List<IModel>
    }

    void testGetParentsWithClassWorksWithLooseMatch() {
        assert this.model.getParents(Super, false) ==
            [this.subCls, this.superCls] as List<IModel>
    }

    void testGetParentsWithBlockingClosureResultsInEmptyList() {
        Closure block = { item, result -> false }
        assert this.model.getParents(Super, false, block).size == 0
    }

    void testGetParentsWithFilteringClosure() {
        Closure onlySuper = { item, result ->
            (item.class == Super)
        }
        assert this.model.getParents(Super, false, onlySuper) ==
            [this.superCls] as List<IModel>
    }

    void testGetParentsReturnsListWithClosestParentFirstRootLast() {
        assert this.model.getParents() ==
            [this.model.parent, this.model.parent.parent] as List<IModel>
    }
}
