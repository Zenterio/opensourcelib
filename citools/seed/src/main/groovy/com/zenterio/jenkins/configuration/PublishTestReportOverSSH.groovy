package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class PublishTestReportOverSSH extends PublishOverSSH {

    /**
     * Name to identify the publication
     */
    String name

    /**
     * Glob pattern to match the report files that should be published
     */
    String reportFilePattern

    /**
     * Part of artifacts path that should be removed in the file transfer.
     */
    String removePrefix

    /**
     * Customer friendly name for the test suite
     */
    String suiteName

    public PublishTestReportOverSSH(Boolean enabled, String name, String server,
            String reportFilePattern, String removePrefix, String suiteName,
            Integer retryTimes, Integer retryDelay, String label) {
        super(enabled, server, retryTimes, retryDelay, label, null)
        this.name = name
        this.reportFilePattern = reportFilePattern
        this.removePrefix = removePrefix ?: ""
        this.suiteName = suiteName
    }

    public PublishTestReportOverSSH(PublishTestReportOverSSH other) {
        super(other)
        this.name = other.name
        this.reportFilePattern = other.reportFilePattern
        this.removePrefix = other.removePrefix
        this.suiteName = other.suiteName
    }

    public PublishTestReportOverSSH clone() {
        return new PublishTestReportOverSSH(this)
    }

    public static PublishTestReportOverSSH getTestData() {
        return new PublishTestReportOverSSH(true, "name", "server",
            "testreport.xml", null, "suite", null, null, null)
    }

}
