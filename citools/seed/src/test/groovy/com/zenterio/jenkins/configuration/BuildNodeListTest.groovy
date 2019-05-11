package com.zenterio.jenkins.configuration

class BuildNodeListTest extends GroovyTestCase {

    public void testDeepClone() {
        def lst = BuildNodeList.testData
        def clone = lst.clone()
        assert lst == clone
        assert !lst.is(clone)
        lst.eachWithIndex { BuildNode original, int i ->
            assert original == clone[i]
            assert !original.is(clone[i])
        }
    }

    public void testGetLabelExpressionMultipleEntries() {
        def lst = BuildNodeList.testData
        assert lst.getLabelExpression() == BuildNode.testData.label + " || " + BuildNode.testData.label
    }

    public void testGetLabelExpressionSingleEntry() {
        def lst = [BuildNode.testData] as BuildNodeList
        assert lst.getLabelExpression() == BuildNode.testData.label
    }

    public void testGetLabelExpressionEmpty() {
        def lst = new BuildNodeList()
        assert lst.getLabelExpression() == ""
    }

}
