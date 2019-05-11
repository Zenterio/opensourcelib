package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@AutoClone
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class Jasmine extends BaseConfig {

    String repository
    String configFile
    String url
    Boolean disableRCU
    Boolean disableRCUCheck

    public Jasmine(String repository, String configFile, String url=null, Boolean disableRCU=true, Boolean disableRCUCheck=true) {

        this.repository = repository?: ''
        if(this.repository == '') {
            throw new IllegalArgumentException('repository is a required argument for Jasmine objects.')
        }

        this.configFile = configFile ?: ''
        if(this.configFile == '') {
            throw new IllegalArgumentException('configFile is a required argument for Jasmine objects.')
        }
        this.url = url
        this.disableRCU = disableRCU ?: false
        this.disableRCUCheck = disableRCUCheck ?: false
    }

    public static Jasmine getTestData() {
        return new Jasmine('repo', 'conf.json','URL', true, true)
    }
}
