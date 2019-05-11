package com.zenterio.jenkins

import com.zenterio.jenkins.configuration.TestContext
import com.zenterio.jenkins.jobtype.*
import com.zenterio.jenkins.configuration.BuildNodeList

/**
 * The JobLabel class is a kind of label factory class in the sense that it
 * provide the build node label depending on job type. It uses polymorphism
 * via different constructors to decide which label to apply. By default the
 * most generic version "JobType" is used. If a more specific type need to
 * be defined, create a constructor with the specific type as parameter.
 * The JobType is not used for anything else than to determine the label.
 *
 */
class JobLabel {

    private String label

    private final String ARTIFACT_COLLECTION = 'artifact-collection'
    private final String DEFAULT = 'default'
    private final String INCREMENTAL = 'incremental'
    private final String PACKAGING = 'release-packaging'
    private final String SIGN = 'sign'
    private final String UTILITY = 'utility'

    /**
     * Default version, all job types except if more specific constructor exist.
     * @param jt
     */
    public JobLabel(JobType jt) {
        this.label = DEFAULT
    }

    public JobLabel(JobType jt, BuildNodeList buildNodes) {
        this.label = buildNodes.getLabelExpression() ?: DEFAULT
    }

    public JobLabel(JobTypeIncrementalCompile jt) {
        this.label = INCREMENTAL
    }

    public JobLabel(JobTypeIncrementalCompile jt, BuildNodeList buildNodes) {
        this.label = buildNodes.getLabelExpression() ?: INCREMENTAL
    }

    public JobLabel(JobTypeSignBuild jt) {
        this.label = SIGN
    }

    public JobLabel(JobTypeReleasePackaging jt) {
        this.label = PACKAGING
    }

    public JobLabel(JobTypeCollectArtifacts jt) {
        this.label = ARTIFACT_COLLECTION
    }

    public JobLabel(JobTypeTestBuild jt, TestContext testContext) {
        this.label = testContext.stbLabel
    }

    public JobLabel(JobTypeIncrementalTestBuild jt, TestContext testContext) {
        this.label = testContext.stbLabel
    }

    public JobLabel(JobTypePromoteBuildChain jt) {
        this.label = UTILITY
    }

    public JobLabel(JobTypeTagBuild jt) {
        this.label = UTILITY
    }

    public JobLabel(JobTypeFlash jt) {
        this.label = UTILITY
    }

    public getLabel() {
        return this.label
    }
}
