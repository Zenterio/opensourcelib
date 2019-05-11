package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.RetentionPolicy
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

/**
 * The purpose of this class is to hold all contact information variables that
 * are inherited across the configuration structure types.
 * This to reduce code duplication associated with all feature and
 * property configuration objects that need to be accessible across
 * all types.
 */
@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
abstract class BaseStructureConfig extends BaseConfig
        implements IPublisherOverSSH, IVariableContext {

    // Attributes
    String name
    PublishOverSSHList publishOverSSHList
    BuildTimeout buildTimeout
    ConcurrentBuilds concurrentBuilds
    RetentionPolicy retentionPolicy
    Resources resources
    VariableCollection variables
    WorkspaceBrowsing workspaceBrowsing
    Priority priority
    // Contactinformation
    ProjectManager pm
    TechLead techLead
    ContactInformationCollection watchers

    /**
     * Default constructor
     */
    public BaseStructureConfig() {
        super()
        this.name = null
        this.pm = null
        this.techLead = null
        this.variables = new VariableCollection()
        this.watchers = new ContactInformationCollection()
        this.publishOverSSHList = new PublishOverSSHList()
        this.resources = null
        this.retentionPolicy = null
        this.buildTimeout = null
        this.concurrentBuilds = null
        this.workspaceBrowsing = null
        this.priority = null
    }

    /**
     * Copy constructor
     * @param other
     */
    public BaseStructureConfig(BaseStructureConfig other) {
        super(other)
        this.name = other.name
        this.pm = other.pm?.clone()
        this.techLead = other.techLead?.clone()
        this.watchers = other.watchers?.clone()
        this.publishOverSSHList = other.publishOverSSHList?.clone()
        this.buildTimeout = other.buildTimeout?.clone()
        this.concurrentBuilds = other.concurrentBuilds?.clone()
        this.retentionPolicy = other.retentionPolicy?.clone()
        this.resources = other.resources?.clone()
        this.variables = other.variables?.clone()
        this.workspaceBrowsing = other.workspaceBrowsing?.clone()
        this.priority = other.priority
    }

    public ContactInformationCollection getAllContacts() {
        return (([this.pm, this.techLead] - null) as ContactInformationCollection) + this.watchers
    }

    /**
     * The other watchers are assumed to come from higher up in the configuration
     * hierarchy and are therefore placed first in the final list.
     * @param otherWatchers
     */
    public void addWatchers(ContactInformationCollection otherWatchers) {
        this.watchers = otherWatchers + this.watchers
    }

    public VariableCollection getVariables() {
        return this.variables
    }

    public void setVariables(VariableCollection collection) {
        this.variables = collection
    }

}
