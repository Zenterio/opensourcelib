package com.zenterio.jenkins.configuration

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class Doc extends BaseConfig implements IPublisherOverSSH, IVariableContext {

    // Properties
    Boolean enabled
    BuildEnv buildEnv
    BuildTimeout buildTimeout
    CredentialList credentials
    CustomBuildStepList customBuildSteps
    MakePrefix makePrefix
    MakeRoot makeRoot
    MakeTarget makeTarget
    Priority priority


    /**
     * A collection of publish over SSH features.
     */
    PublishOverSSHList publishOverSSHList

    Resources resources

    VariableCollection variables

    /**
     * Null enabled is replaced by false.
     *
     * @param enabled   If documentation generation should be enabled or not.
     *
     */
    public Doc(Boolean enabled = true) {
        this.enabled = enabled ?: false
        this.buildTimeout = null
        this.credentials = new CredentialList()
        this.customBuildSteps = new CustomBuildStepList()
        this.makePrefix = null
        this.makeRoot = null
        this.makeTarget = null
        this.priority = null
        this.publishOverSSHList = new PublishOverSSHList()
        this.resources = null
        this.variables = new VariableCollection()
        this.buildEnv = null
    }

    /**
     * Copy constructor
     * @param other
     */
    public Doc(Doc other) {
        super(other)
        this.enabled = other.enabled
        this.buildTimeout = other.buildTimeout?.clone()
        this.credentials = other.credentials?.clone()
        this.customBuildSteps = other.customBuildSteps?.clone()
        this.makePrefix = other.makePrefix?.clone()
        this.makeRoot = other.makeRoot?.clone()
        this.makeTarget = other.makeTarget?.clone()
        this.priority = other.priority
        this.publishOverSSHList = other.publishOverSSHList?.clone()
        this.resources = other.resources?.clone()
        this.variables = other.variables?.clone()
        this.buildEnv = other.buildEnv?.clone()
    }

    public Object clone() throws CloneNotSupportedException {
        return new Doc(this)
    }

    public static Doc getTestData() {
        Doc doc = new Doc(true)
        doc.buildTimeout = BuildTimeout.testData
        doc.credentials = CredentialList.testData
        doc.customBuildSteps.add(CustomBuildStep.testData)
        doc.makePrefix = MakePrefix.testData
        doc.makeRoot = MakeRoot.testData
        doc.makeTarget = MakeTarget.testData
        doc.priority = Priority.MEDIUM
        doc.publishOverSSHList = PublishOverSSHList.testData
        doc.resources = Resources.testData
        doc.variables = VariableCollection.testData
        doc.buildEnv = BuildEnv.testData
        return doc
    }
}
