package com.zenterio.jenkins.models

class JoinModelTest extends GroovyTestCase {

    IModel join
    IModel parent1
    IModel parent2
    IModel child1
    IModel child2

    @Override
    void setUp() throws Exception {
        this.join = new JoinModel()
        this.parent1 = new ModelEntity()
        this.parent2 = new ModelEntity()
        this.child1 = new ModelEntity()
        this.child2 = new ModelEntity()
    }

    void testFirstParentIsAddedAsNormal() {
        this.parent1 << this.join

        assert this.join.parent == this.parent1
        assert this.parent1.children[0] == this.join
    }

    void testSecondParentIsAddedAsExtraParent() {
        this.parent1 << this.join
        this.parent2 << this.join

        assert this.join.parent == this.parent1
        assert this.parent1.children[0] == this.join
        assert this.join.extraParents.contains(this.parent2)
        assert this.parent2.children[0] == this.join
    }

    void testSecondParentTriggersOnSetParentEvent() {
        int called = 0
        this.join.regOnSetParentEventHandler({ p, c -> called++ })

        this.parent1 << this.join
        this.parent2 << this.join

        assert called == 2
    }

    void testParentsAreOnlyAddedOnce() {
        this.join.with {
            it.setParent(this.parent1)
            it.setParent(this.parent2)
            it.setParent(this.parent1)
            it.setParent(this.parent2)
        }

        assert this.parent1.children.size == 1
        assert this.join.extraParents.size == 1
        assert this.parent2.children.size == 1
    }

    void testSecondParentCanBeUnsetAndTriggersUnsetParentEvent() {
        int called = 0
        this.parent1 << this.join
        this.parent2 << this.join
        this.join.regOnUnsetParentEventHandler({ p, c -> called++ })

        assert this.parent2 == this.join.unsetParent(this.parent2)
        assert called == 1
    }

    void testGetChildrenOnlyReturnOneEntryForEachChild() {
        this.parent1 << this.join
        this.parent2 << this.join
        this.join << this.child1
        this.join << this.child2
        IModel root = new ModelEntity()
        root << this.parent1
        root << this.parent2

        List<IModel> children = root.getChildren(ModelEntity, false, true)
        assert children.size() == 4
    }
}

