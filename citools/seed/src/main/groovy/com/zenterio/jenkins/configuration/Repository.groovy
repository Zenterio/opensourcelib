package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.Utils
import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class Repository extends BaseConfig {

    String name
    String directory
    String remote
    String branch
    String envName
    Boolean allowTags
    Boolean allowNotifyCommit
    Boolean configurable

    Repository(String name, String directory, String remote, String branch,
            Boolean configurable) {
        this.name = name;
        this.directory = directory;
        this.remote = remote;
        this.branch = branch;
        this.configurable = configurable
        this.envName = Utils.safeVariableNameUpperCase(this.name)
        this.allowTags = true
        this.allowNotifyCommit = true

    }

    public static Repository getTestData() {
        return new Repository("REPOSITORY-NAME", "DIRECTORY", "git@REMOTE:repo", "BRANCH", null)
    }

    public String toShortString() {
        return "${this.name} ${this.remote}"
    }

    @Override
    public String toString(){
        return "${this.name} ${this.directory} ${this.remote} ${this.branch}"
    }
}
