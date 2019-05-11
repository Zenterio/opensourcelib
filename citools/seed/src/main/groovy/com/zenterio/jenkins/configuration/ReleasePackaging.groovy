package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class ReleasePackaging extends BaseConfig implements IPublisherOverSSH, IVariableContext {

    /**
     * True if release and tag values is configurable by user
     */
    Boolean configurable

    /**
     * True if release packaging should be offered at all.
     */
    Boolean enabled

    /**
     * To specify the timeout of the job generated from this config
     */
    BuildTimeout buildTimeout

    /**
     * Credential list
     */
    CredentialList credentials

    /**
     * Custom build steps to override default.
     */
    CustomBuildStepList customBuildSteps

    /**
     * Extra description
     */
    Description description

    /**
     * Override LogParsing config
     */
    LogParsing logParsing

    /**
     * A collection of publish over SSH features.
     */
    PublishOverSSHList publishOverSSHList

    Resources resources

    /**
     * Repositories
     */
    Repository[] repositories

    VariableCollection variables

    /**
     * null enabled is replaced by false.
     *
     * @param enabled   If release packaging should be enabled or not.
     *
     */
    ReleasePackaging(Boolean configurable, Boolean enabled = true) {
        this.configurable = configurable ?: false
        this.enabled = enabled ?: false
        this.customBuildSteps = new CustomBuildStepList()
        this.publishOverSSHList = new PublishOverSSHList()
        this.buildTimeout = null
        this.description = null
        this.logParsing = null
        this.credentials = new CredentialList()
        this.resources = null
        this.repositories = new Repository[0]
        this.variables = new VariableCollection()
    }

    /**
     * Copy constructor
     * @param other
     */
    ReleasePackaging(ReleasePackaging other) {
        this.configurable = other.configurable
        this.enabled = other.enabled
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.buildTimeout = other.buildTimeout?.clone()
        this.publishOverSSHList = other.publishOverSSHList?.clone()
        this.description = other.description?.clone()
        this.logParsing = other.logParsing?.clone()
        this.credentials = other.credentials?.clone()
        this.resources = other.resources?.clone()
        this.repositories = other.repositories.collect { r -> r?.clone() } as Repository[]
        this.variables = other.variables?.clone()
    }

    public Object clone() throws CloneNotSupportedException {
        return new ReleasePackaging(this)
    }

    public static ReleasePackaging getTestData() {
        ReleasePackaging data = new ReleasePackaging(true, true)
        data.buildTimeout = BuildTimeout.testData
        data.credentials = CredentialList.testData
        data.customBuildSteps.add(CustomBuildStep.testData)
        data.description = Description.testData
        data.logParsing = LogParsing.testData
        data.publishOverSSHList = PublishOverSSHList.testData
        data.resources = Resources.testData
        data.repositories = [Repository.testData] as Repository[]
        data.variables = VariableCollection.testData
        return data
    }

}
