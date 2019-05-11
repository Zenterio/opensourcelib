package com.zenterio.jenkins.configuration

public enum TestReportType {
    JUNIT('junit'),
    TESTNG('testng')

    public final String name

    private TestReportType(String name) {
        this.name = name
    }

    @Override
    String toString() {
        return name
    }
}