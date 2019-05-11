package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
class Resources extends BaseConfig {

    final Boolean enabled

    /**
     * Resource name
     */
    String name

    /**
     * Resource name
     */
    String label

    /**
     * Specifies how many of the resource that are requested
     */
    Integer quantity

    Resources(Boolean enabled, String name, String label, Integer quantity) {
        this.enabled = enabled
        this.name = name
        this.label = label
        this.quantity = quantity

        if (this.enabled) {
            if (this.name == null && this.label == null) {
                throw new ConfigError("One of name or label needs to be specified in: ${node}")
            }
            if (this.name != null && this.label != null) {
                throw new ConfigError("Only one of name and label allowed in: ${node}")
            }
        }
    }

    public static Resources getTestData() {
        Resources data = new Resources(true, "RESOURCE-NAME", null, 2)
        return data
    }
}
