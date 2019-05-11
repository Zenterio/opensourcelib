package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class BuildNodeList extends ArrayList<BuildNode> {

    @Override
    public BuildNodeList clone() {
        return this.collect{ BuildNode buildNode ->
            buildNode.clone()
        } as BuildNodeList
    }

    public String getLabelExpression() {
        return this.collect( { BuildNode bn -> bn.label } ).join(" || ")
    }

    public static BuildNodeList getTestData() {
        return [BuildNode.testData,
                BuildNode.testData] as BuildNodeList
    }
}
