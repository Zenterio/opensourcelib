package com.zenterio.jenkins

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(includeFields=true)
@AutoClone
public class RetentionPolicy {

    final RetentionPolicyType type
    final boolean saveArtifacts

    public RetentionPolicy(RetentionPolicyType type, boolean saveArtifacts) {
        this.type = type
        this.saveArtifacts = saveArtifacts
    }

    public getDaysToKeep() {
        return -1
    }

    public getNumToKeep() {
        return this.type.value
    }

    public getArtifactDaysToKeep() {
        return -1
    }

    public getArtifactNumToKeep() {
        return this.saveArtifacts ? this.type.value : 1
    }

    public static getTestData() {
        return new RetentionPolicy(RetentionPolicyType.SHORT, false)
    }
}
