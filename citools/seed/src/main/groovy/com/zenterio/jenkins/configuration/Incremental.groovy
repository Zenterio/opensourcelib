package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Incremental extends BaseConfig implements IVariableContext, ITester {

    Boolean enabled
    BuildNodeList buildNodes
    Cache cache
    TestGroup[] testGroups
    Resources resources
    VariableCollection variables

    /**
     * Null enabled is replaced by false.
     *
     * The default is to have incremental builds enabled.
     *
     * @param enabled   If incremental builds should be enabled.
     *
     */
    Incremental(Boolean enabled) {
        this.enabled = enabled ?: false
        this.buildNodes = new BuildNodeList()
        this.cache = null
        this.testGroups = new TestGroup[0]
        this.resources = null
        this.variables = new VariableCollection()
    }

    public static Incremental getTestData() {
        Incremental data = new Incremental(true)
        data.cache = Cache.testData
        data.buildNodes = BuildNodeList.testData
        data.resources = Resources.testData
        data.variables = VariableCollection.testData
        data.testGroups = [TestGroup.testData] as TestGroup[]
        return data
    }
}
