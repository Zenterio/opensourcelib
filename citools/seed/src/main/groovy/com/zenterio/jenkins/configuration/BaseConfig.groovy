package com.zenterio.jenkins.configuration

import groovy.transform.Canonical

/**
 * All configuration classes should inherit from this class.
 */
@Canonical
class BaseConfig {

    /**
     * Default constructor
     */
    public BaseConfig() {

    }

    /**
     * Copy constructor
     * @param other
     */
    public BaseConfig(BaseConfig other) {

    }

    /**
     * The inherit() function is a clone()-like method that may override some values.
     * It is used in the seed config resolver.
     * @return A new item with possibly some value reset.
     * @throws CloneNotSupportedException
     */
    public BaseConfig inherit() throws CloneNotSupportedException {
        return this.clone()
    }
}
