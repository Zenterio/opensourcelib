package com.zenterio.jenkins.configuration

class VariableCollectionTest extends GroovyTestCase {

    public void testDeepCloneEquals() {
        VariableCollection collection = VariableCollection.testData
        VariableCollection clone = collection.clone()

        assert collection == clone
        assert !collection.is(clone)
        assert collection[0] == clone[0]
        assert !collection[0].is(clone[0])

        clone.add(Variable.testData)
        assert collection != clone
    }

    public void testGetValue() {
        VariableCollection collection = VariableCollection.testData
        assert collection.getValue("var1") == "value1"
        assert collection.getValue("var2") == "value2"
        assert collection.getValue("does not exist") == null
    }

    public void testInheritFrom() {
        VariableCollection collection = VariableCollection.testData
        VariableCollection other = new VariableCollection()
        other.add(new Variable("var2", "new value"))
        other.add(new Variable("var3", "other value"))
        other.inheritFrom(collection)
        assert collection != other
        assert other.getValue("var1") == "value1"
        assert other.getValue("var2") == "new value"
        assert other.getValue("var3") == "other value"
    }

}
