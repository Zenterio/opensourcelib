package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class LogParsing extends BaseConfig {
    String configurationFile
    Boolean enabled

    public LogParsing(String configurationFile, Boolean enabled) {
        this.configurationFile = configurationFile
        this.enabled = enabled
    }

    public static LogParsing getTestData() {
        return new LogParsing("config", true)
    }
}
