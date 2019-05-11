package com.zenterio.jenkins.jobtype

import groovy.transform.EqualsAndHashCode

/**
 * The class is made abstract to indicate that the class
 * should not be instantiated.
 */
@EqualsAndHashCode(includeFields=true)
abstract public class JobType {

    final String name;
    final String shortName;
    final String description;

    protected JobType(String name, String shortName, String description) {
        this.name = name;
        this.shortName = shortName;
        this.description = description;
    }

    @Override
    public String toString() {
        return this.name;
    }

};
