package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class TestCommandArgs extends BaseConfig {
    String extraArgs

    public TestCommandArgs(String extraArgs) {
        this.extraArgs = extraArgs
    }

    public static TestCommandArgs getTestData() {
        return new TestCommandArgs("--extra_args arguments")
    }
}
