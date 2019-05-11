package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
class BuildNode extends BaseConfig {

    /**
     * Build node label
     */
    final String label

    BuildNode(String label) {
        this.label = label
    }

    public static BuildNode getTestData() {
        BuildNode data = new BuildNode("NODE-LABEL")
        return data
    }
}
