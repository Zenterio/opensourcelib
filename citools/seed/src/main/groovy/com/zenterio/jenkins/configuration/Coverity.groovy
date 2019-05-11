package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.buildtype.BuildType
import com.zenterio.jenkins.buildtype.BuildTypeDebug
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class Coverity extends BaseConfig implements IPublisherOverSSH, IVariableContext {

    /**
     * Name of coverity stream to push data analysis to.
     */
    String stream

    /**
     * True if coverity feature turned on and coverity job should be generated.
     */
    Boolean enabled

    Upstream upstream
    String periodic

    /**
     * Level of aggressiveness used during analysis step.
     */
    Aggressiveness aggressiveness

    /**
     * Buildtype to run coverity on
     */
    BuildType buildType

    /**
     * Credential list for this configuration.
     */
    CredentialList credentials

    /**
     * Custom build steps to override default.
     */
    CustomBuildStepList customBuildSteps

    /**
     * A collection of publish over SSH features.
     */
    PublishOverSSHList publishOverSSHList

    /**
     * To specify the timeout of the job generated from this config
     */
    BuildTimeout buildTimeout

    Resources resources

    VariableCollection variables

    WorkspaceBrowsing workspaceBrowsing

    Priority priority

    BuildEnv buildEnv

    /**
     * Null stream is replaced by empty string; null enabled is replaced by false.
     * Combination of unspecified stream and enabled is allowed.
     *
     * @param stream    The name of the stream to push data analysis to
     * @param enabled   If Coverity should be enabled or not.
     * @param upstream  Defines how job will be triggered, if it will be part of the build flow
     * @param periodic  Cron string job trigger frequency, used with upstream=false
     * @param aggressiveness   Level of aggressiveness used for analysis
     *
     */
    Coverity(String stream, Boolean enabled, Upstream upstream, String periodic, Aggressiveness aggressiveness, BuildType buildType) {
        this.stream = stream ?: ""
        this.enabled = enabled
        this.upstream = upstream
        this.periodic = periodic
        this.aggressiveness = aggressiveness
        this.buildType = buildType
        this.credentials = new CredentialList()
        this.customBuildSteps = new CustomBuildStepList()
        this.publishOverSSHList = new PublishOverSSHList()
        this.buildTimeout = null
        this.resources = null
        this.variables = new VariableCollection()
        this.workspaceBrowsing = null
        this.priority = null
        this.buildEnv = null
    }

    /**
     * Copy constructor
     * @param other
     */
    Coverity(Coverity other) {
        this.stream = other.stream
        this.enabled = other.enabled
        this.upstream = other.upstream
        this.periodic = other.periodic
        this.aggressiveness = other.aggressiveness
        this.buildType = other.buildType
        this.credentials = other.credentials?.clone()
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.publishOverSSHList = other.publishOverSSHList?.clone()
        this.buildTimeout = other.buildTimeout?.clone()
        this.resources = other.resources?.clone()
        this.variables = other.variables?.clone()
        this.workspaceBrowsing = other.workspaceBrowsing?.clone()
        this.priority = other.priority
        this.buildEnv = other.buildEnv?.clone()
    }

    public Object clone() throws CloneNotSupportedException {
        return new Coverity(this)
    }

    public static Coverity getTestData() {
        Coverity data = new Coverity("STREAM", true, Upstream.TRUE, "", Aggressiveness.LOW, new BuildTypeDebug())
        data.buildTimeout = BuildTimeout.testData
        data.credentials = CredentialList.testData
        data.customBuildSteps.add(CustomBuildStep.testData)
        data.publishOverSSHList = PublishOverSSHList.testData
        data.resources = Resources.testData
        data.variables = VariableCollection.testData
        data.workspaceBrowsing = WorkspaceBrowsing.testData
        data.priority = Priority.MEDIUM
        data.buildEnv = BuildEnv.testData
        return data
    }

}
