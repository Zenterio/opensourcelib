package com.zenterio

import com.zenterio.jenkins.configuration.*

class ObjectVisitorTest extends GroovyTestCase {

    RootType root
    ObjectVisitor<RootType> visitor
    TestActionVisit action
    int visitIndex

    @Override
    protected void setUp() {
        this.root = this.getTestData()
        this.action = new TestActionVisit()
        this.visitor = new ObjectVisitor<RootType>(action, RootType.class)
        this.visitIndex = 0
    }

    protected RootType getTestData() {
        RootType r = new RootType()
        r.with {
            arr = [new Object()] as Object[]
            map = ["A": 1]
            ref = new RootType()
            strField = "A"
            booleanField = true
        }
        r.ref.with {
            arr = [new Object()] as Object[]
            map = ["B": 2]
            ref = new RootType()
            strField = "B"
            booleanField = false
        }
        r.ref.ref.with {
            arr = [new Object()] as Object[]
            map = ["C": 3]
            ref = new RootType()
            strField = "C"
            booleanField = true

        }
        return r
    }

    public void visit(Object obj) {
        this.visitor.visit(obj)
        assert this.action.visitors[this.visitIndex] == obj
        this.visitIndex += 1
    }

    public void testVisitString() {
        this.visit("s")
        this.visit("")
    }

    public void testVisitBoolean() {
        this.visit(true)
        this.visit(false)
    }

    public void testVisitInteger() {
        this.visit(0)
        this.visit(1)
    }

    public void testVisitMap() {

    }

    public void testVisitArray() {
        Object o1 = new Object()
        Object o2 = new Object()
        Object[] arr = [o1, o2]
        this.visitor.visit(arr)
        assert this.action.visitors[0] == o1
        assert this.action.visitors[1] == o2
    }

    public void testVisitNativeTypeArray() {
        /* Native type arrays are transformed into lists in groovy
         * when trying to accomodate the interface of the visitor
         * and it will be transformed as though it was a single object.
         * Very annoying!
         */
         int[] arr = new int[2]
         arr[0] = 1
         arr[1] = 2
         this.visitor.visit(arr)
         this.action.visitors[0][1] == 2
    }
    public void testVisitNativeTypeArrayCohersedIntoList() {
        /* Native type arrays are transformed into lists in groovy
         * when trying to accomodate the interface of the visitor
         * and it will be transformed as though it was a single object.
         * Very annoying!
         */
         int[] arr = new int[2]
         arr[0] = 1
         arr[1] = 2
         this.visitor.visit(arr as List<Integer>)
         assert this.action.visitors[0] == arr
         assert this.action.visitors[1] == 1
         assert this.action.visitors[2] == 2
    }

    public void testVisitList() {
        this.visit(new ArrayList<String>(["A", "B"]))
        assert this.action.visitors[1] == "A"
        assert this.action.visitors[2] == "B"
    }

    public void testContext() {
        this.visit(this.root)
        assert this.action.contexts[0].size == 0
        assert this.action.contexts[1].size == 1
        assert this.action.contexts[1][0] == this.root
    }

    public void testPropertyName() {
        this.visitor.visit(this.root)
        assert this.action.propertyNames[0] == null
        assert this.action.propertyNames[1] == "arr" // arr - first property
        assert this.action.propertyNames[2] == "[0]" // index 0 in arr
        assert this.action.propertyNames[3] == "booleanField" // second poperty
        assert this.action.propertyNames[4] == "list" // third poperty
        assert this.action.propertyNames[5] == "[0]" // index 0 in list
        assert this.action.propertyNames[6] == "map" // forth property
        assert this.action.propertyNames[7] == "[A]" // first key in map
    }

    public void testVisitPreventInfiniteRecursion() {
        RootType first = new RootType()
        RootType second = new RootType()
        first.ref = second
        first.strField = "FIRST"
        second.ref = first
        second.strField = "SECOND"
        this.visitor.visit(first)
        // 5 properties (array not added to visitors) + 1 (list item)
        // the root element, also appearing as reference is not counted.
        assert this.action.visitors.size == (2*(5+1))
    }
}

class RootType  {
    Object[] arr
    Map map
    boolean booleanField
    String strField
    RootType ref
    List<String> list

    RootType() {
        this.arr = new Object[0]
        this.map = [:]
        this.list = new ArrayList<String>()
        this.list.add("LIST")
    }
}

class TestActionVisit implements IActionVisit<RootType> {

    List<Object> visitors
    List< List<RootType> > contexts
    List<String> propertyNames

    public TestActionVisit() {
        this.visitors = new ArrayList<Object>()
        this.contexts = new ArrayList< List<RootType> >()
        this.propertyNames = new ArrayList<String>()
    }

    public void perform(Object obj, List<RootType> context, String propertyName) {
        if (context.size > 10) {
            // arbitrary large context, indicates infinite recursion
            throw new RuntimeException("Large context - infinite recursion?")
        }
        this.visitors.add(obj)
        this.contexts.add(context)
        this.propertyNames.add(propertyName)
    }
    public void perform(Object[] arr, List<RootType> context, String propertyName) {
        this.propertyNames.add(propertyName)
        this.contexts.add(context)
    }
}
