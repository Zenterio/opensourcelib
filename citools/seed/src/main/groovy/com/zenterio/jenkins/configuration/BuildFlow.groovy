package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class BuildFlow extends BaseConfig {

    BuildFlowStyle style

    BuildFlow(BuildFlowStyle style) {
        this.style = style
    }

    public static BuildFlow getTestData() {
        return new BuildFlow(BuildFlowStyle.ZIDS_UNIT_TEST_PARALLEL)
    }
}
