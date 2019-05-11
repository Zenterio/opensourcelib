package com.zenterio.jenkins.configuration

public enum CustomBuildStepType {
    SHELL('shell'),
    SYSTEM_GROOVY('system-groovy')

    public final String name

    private CustomBuildStepType(String name) {
        this.name = name
    }

    @Override
    String toString() {
        return name
    }
}