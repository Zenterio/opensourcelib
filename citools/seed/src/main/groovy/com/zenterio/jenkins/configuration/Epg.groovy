package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Epg extends BaseConfig {
    String path

    public Epg(String path) {
        this.path = path
    }

    public static Epg getTestData() {
        return new Epg("test_epg.tar.gz")
    }
}
