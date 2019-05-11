package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class PublishBuildOverSSH extends PublishOverSSH {

    /**
     * Name to identify the publication
     */
    String name

    /**
     * ANT file-set pattern to match the artifacts that should be published
     */
    String artifactPattern

    /**
     * Part of artifacts path that should be removed in the file transfer.
     */
    String removePrefix

    /**
     * Root directory on the publishing server, where to store the published
     * content. The total path will be: rootDir/productAltName/buildType/date-id/
     */
    String rootDir

    /**
     * Alternative product name, customer friendly short form, of the product
     * name. Defaults to the original product name in lowercase.
     */
    String productAltName

    /**
     * Number of builds to keep. Defaults to 5.
     */
    Integer numberOfBuildsToKeep

    public PublishBuildOverSSH(Boolean enabled, String name, String server,
            String artifactPattern, String removePrefix,
            String rootDir, Integer numberOfBuildsToKeep,
            String productAltName,
            Integer retryTimes, Integer retryDelay, String label) {
        super(enabled, server, retryTimes, retryDelay, label, null)
        this.name = name
        this.artifactPattern = artifactPattern
        this.removePrefix = removePrefix ?: ""
        this.rootDir = rootDir
        this.numberOfBuildsToKeep = numberOfBuildsToKeep ?: 5
        this.productAltName = productAltName ?: '${product_alt_name}'
    }

    public PublishBuildOverSSH(PublishBuildOverSSH other) {
        super(other)
        this.name = other.name
        this.artifactPattern = other.artifactPattern
        this.removePrefix = other.removePrefix
        this.rootDir = other.rootDir
        this.numberOfBuildsToKeep = other.numberOfBuildsToKeep
        this.productAltName = other.productAltName

    }

    public PublishBuildOverSSH clone() {
        return new PublishBuildOverSSH(this)
    }

    public static PublishBuildOverSSH getTestData() {
        return new PublishBuildOverSSH(true, "name", "server",
            "image", null, "/directory", 5, "product",
            null, null, null)
    }

}
