package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Description extends BaseConfig {

    String description

    /**
     * Extra description for projects, origins and products.
     *
     * @param description Extra description to add to Jenkins page
     *
     */
    Description(String description = null) {
        this.description = description
    }

    public static Description getTestData() {
        return new Description("Test Description")
    }
}
