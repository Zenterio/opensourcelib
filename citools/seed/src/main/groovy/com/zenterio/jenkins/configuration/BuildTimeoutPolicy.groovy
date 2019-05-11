package com.zenterio.jenkins.configuration

public enum BuildTimeoutPolicy {
    ABSOLUTE('absolute'),
    ELASTIC('elastic'),

    public final String name

    private BuildTimeoutPolicy(String name) {
        this.name = name
    }
}
