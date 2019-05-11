package com.zenterio.jenkins.configuration.macroexpansion

import java.beans.PropertyDescriptor

import com.zenterio.jenkins.configuration.*

class WalkerTest extends GroovyTestCase {

    RootType root
    ObjectVisitor<RootType> visitor

    @Override
    protected void setUp() {
        this.root = this.getTestData()
        this.visitor = new ObjectVisitor<RootType>(new TestTransform(), RootType.class)
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

    public void testIsMap() {
        assert this.visitor.isMap([:]) == true
        assert this.visitor.isMap([]) == false
    }

    public void testIsCollection() {
        assert this.visitor.isCollection([]) == true
        assert this.visitor.isCollection(new ArrayList<Integer>()) == true
        assert this.visitor.isCollection(new Object()) == false
        assert this.visitor.isCollection(new Object[0]) == false
    }

    public void testIsArray() {
        assert this.visitor.isArray(new Object[0]) == true
        assert this.visitor.isArray(new int[0]) == true
        assert this.visitor.isArray(new Object()) == false
        assert this.visitor.isArray(new ArrayList<Integer>()) == false
        assert this.visitor.isArray([]) == false
        assert this.visitor.isArray([:]) == false
    }

    public void testWalkString() {
        this.visitor.visit(this.root)
        assert this.root.strField == 'a'
        assert this.root.ref.strField == 'b'
        assert this.root.ref.ref.strField == 'c'
    }

    public void testWalkBoolean() {
        this.visitor.visit(this.root)
        assert this.root.booleanField == false
        assert this.root.ref.booleanField == true
        assert this.root.ref.ref.booleanField == false
    }

    public void testWalkMapKeysAreUneffected() {
        this.visitor.visit(this.root)
        assert this.root.map["A"] == 5
        assert this.root.ref.map["B"] == 10
        assert this.root.ref.ref.map["C"] == 15
    }

    public void testWalkArray() {
        this.visitor.visit(this.root)
        assert this.root.arr[0] == "Transformed"
        assert this.root.ref.arr[0] == "Transformed"
        assert this.root.ref.ref.arr[0] == "Transformed"
    }

    public void testWalkList() {
        this.visitor.visit(this.root)
        assert this.root.list[0] == "list"
        assert this.root.ref.list[0] == "list"
        assert this.root.ref.ref.list[0] == "list"
    }

    public void testContext() {
        this.visitor.visit(this.root)
        assert this.root.context.size == 0
        assert this.root.ref.context.size == 1
        assert this.root.ref.ref.context.size == 2
    }

    public void testWalkPreventInfiniteRecursion() {
        RootType first = new RootType()
        RootType second = new RootType()
        first.ref = second
        first.strField = "FIRST"
        second.ref = first
        second.strField = "SECOND"
        this.visitor.visit(first)
        assert first.strField == "first"
        assert second.strField == "second"
    }

}

public class RootType  {
    Object[] arr
    Map map
    boolean booleanField
    String strField
    protected List<RootType> context
    RootType ref
    List<String> list

    RootType() {
        this.context = new ArrayList<RootType>()
        this.arr = new Object[0]
        this.map = [:]
        this.list = new ArrayList<String>()
        this.list.add("LIST")
    }

    // Need to use a non-setter not to cause infinite recursion
    public void updateContext(List<RootType> context) {
        this.context = context
    }

}

class TestTransform implements ITransform<RootType> {

    public Object transform(Object obj, List<RootType> context) {
        if (obj == null) {
            return obj
        }
        if (context.size > 10) {
            // arbitrary large context, indicates infinite recursion
            throw new RuntimeException("Large context - infinite recursion?")
        }
        switch (obj.class.getName()) {
            case String.class.getName():
                obj = obj.toLowerCase()
                break
            case Boolean.class.getName():
                obj = !obj
                break
            case Integer.class.getName():
                obj = obj*5
                break
            case RootType.class.getName():
                obj.updateContext(context)
                break
            case Object.class.getName():
                obj = "Transformed"
            default:
                // Do nothing
                break
        }
        return obj
    }
}
