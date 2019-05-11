package com.zenterio.jenkins.models

class BaseModelEventHandling extends GroovyTestCase {

    List<String> triggeredEvents

    class TestModel extends BaseModel {

        public int addedChild = 0
        public int removedChild = 0
        public int settedParent = 0 // misspelling due to name conflict
        public int unsettedParent = 0 // misspelling due to name conflict
        public List<String> triggeredEvents

        TestModel(List<String> triggeredEvents) {
            this.triggeredEvents = triggeredEvents
        }

        @Override
        protected void onAddChild(IModel child) {
            super.onAddChild(child)
            this.addedChild += 1
            this.triggeredEvents.add("onAddChild")
        }

        protected void onRemoveChild(IModel child) {
            super.onRemoveChild(child)
            this.removedChild += 1
            this.triggeredEvents.add("onRemoveChild")
        }

        @Override
        protected void onSetParent(IModel parent) {
            super.onSetParent(parent)
            this.settedParent += 1
            this.triggeredEvents.add("onSetParent")
        }

        @Override
        protected void onUnsetParent(IModel parent) {
            super.onUnsetParent(parent)
            this.unsettedParent += 1
            this.triggeredEvents.add("onUnsetParent")
        }
    }

    TestModel parent
    TestModel child

    @Override
    void setUp() throws Exception {
        this.triggeredEvents = new ArrayList<String>()
        this.parent = new TestModel(this.triggeredEvents)
        this.child = new TestModel(this.triggeredEvents)
    }

    void testAddChildAsStartingPoint() {
        this.parent.addChild(this.child)
        assert this.parent.children[0] == this.child
        assert this.parent.addedChild == 1
        assert this.child.parent == this.parent
        assert this.child.settedParent == 1
        assert this.triggeredEvents[0] == "onAddChild"
        assert this.triggeredEvents[1] == "onSetParent"

    }

    void testRemoveChildAsStartingPoint() {
        this.parent.addChild(this.child)
        this.parent.removeChild(this.child)
        assert this.parent.removedChild == 1
        assert this.child.unsettedParent == 1
        assert this.triggeredEvents[2] == "onRemoveChild"
        assert this.triggeredEvents[3] == "onUnsetParent"
    }

    void testSetParentAsStartingPoint() {
        this.child.setParent(this.parent)
        assert this.parent.children[0] == this.child
        assert this.parent.addedChild == 1
        assert this.child.parent == this.parent
        assert this.child.settedParent == 1
        assert this.triggeredEvents[0] == "onSetParent"
        assert this.triggeredEvents[1] == "onAddChild"

    }

    void  testUnsetParentAsStartingPoint() {
        this.child.setParent(this.parent)
        this.child.unsetParent()
        assert this.child.unsettedParent == 1
        assert this.parent.removedChild == 1
        assert this.triggeredEvents[2] == "onUnsetParent"
        assert this.triggeredEvents[3] == "onRemoveChild"
    }

    void testExternalAddChildEvent() {
        IModel testParent = null
        IModel testChild = null
        Closure handler = this.parent.regOnAddChildEventHandler({ c, p ->
            assert p.children.contains(c)
            testChild = c
            testParent = p
        })
        this.parent << this.child
        assert testParent == this.parent
        assert testChild == this.child

        this.parent.unregOnAddChildEventHandler(handler)
        this.parent.onAddChildEventListeners.size == 0
    }

    void testExternalRemoveChildEvent() {
        IModel testParent = null
        IModel testChild = null
        Closure handler = this.parent.regOnRemoveChildEventHandler({ c, p ->
            assert ! p.children.contains(c)
            testChild = c
            testParent = p
        })

        this.parent << this.child
        this.parent.removeChild(this.child)
        assert testParent == this.parent
        assert testChild == this.child

        this.parent.unregOnRemoveChildEventHandler(handler)
        this.parent.onRemoveChildEventListeners.size == 0
    }

    void testExternalSetParentEvent() {
        IModel testParent = null
        IModel testChild = null
        Closure handler = this.child.regOnSetParentEventHandler({ p, c ->
            assert c.parent == p
            testParent = p
            testChild = c
        })
        this.parent << this.child
        assert testParent == this.parent
        assert testChild == this.child

        this.parent.unregOnSetParentEventHandler(handler)
        this.parent.onSetParentEventListeners.size == 0
    }

    void testExternalUnsetParentEvent() {
        IModel testParent = null
        IModel testChild = null
        Closure handler = this.child.regOnUnsetParentEventHandler({ p, c ->
            assert c.parent == null
            testParent = p
            testChild = c
        })

        this.parent << this.child
        this.parent.removeChild(this.child)
        assert testParent == this.parent
        assert testChild == this.child

        this.parent.unregOnUnsetParentEventHandler(handler)
        this.parent.onUnsetParentEventListeners.size == 0
    }

}
