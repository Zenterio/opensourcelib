package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Image extends BaseConfig {
    String artifact
    Boolean enabled
    Boolean flatten

    public Image(String artifact, Boolean enabled, Boolean flatten) {
        this.artifact = artifact
        this.enabled = enabled ?: false
        this.flatten = flatten
    }

    public static Image getTestData() {
        return new Image("test_kfs.zmg", true, true)
    }
}
