package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Duration extends BaseConfig {

    String time;

    public Duration(String time) {
        this.time = time
    }

    public static Duration getTestData() {
        return new Duration("03:14:15")
    }
}
