package com.zenterio.jenkins.buildtype

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

/**
 * The class is made abstract to indicate that the class
 * should not be instantiated.
 */
@EqualsAndHashCode(includeFields=true)
@Canonical()
@AutoClone
public abstract class BuildType {

    final String name;
    final String shortName;
    final String description;

    /**
     * @param name
     * @param shortName
     * @param description
     */
    public BuildType(String name, String shortName, String description) {
        this.name = name;
        this.shortName = shortName;
        this.description = description;
    }

    @Override
    public String toString() {
        return this.name;
    }

};
