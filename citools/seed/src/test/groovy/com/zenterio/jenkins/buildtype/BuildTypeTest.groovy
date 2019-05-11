package com.zenterio.jenkins.buildtype


import groovy.util.GroovyTestCase;

class BuildTypeTest  extends GroovyTestCase {

    BuildType[] variants = [
        new BuildTypeDebug(),
        new BuildTypeRelease(),
        new BuildTypeProduction(),
        new BuildTypeCustom("name", "sn", "desc")
    ]

    public void testDeepClone() {
        for (BuildType data in variants) {
            BuildType clone = data.clone()
            assert data == clone
            assert !data.is(clone)
        }
    }

    void testToString() {
        for (BuildType bt in variants) {
            assert bt.name == bt.toString()
        }
    }
}
