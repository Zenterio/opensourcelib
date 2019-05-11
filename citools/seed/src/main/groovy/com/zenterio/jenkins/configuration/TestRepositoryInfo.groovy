package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.Utils
import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode


@Canonical
@EqualsAndHashCode(includeFields=true)
@AutoClone
class TestRepositoryInfo {
    String testGroupName
    Repository repository

    public TestRepositoryInfo(String testGroupName, Repository repository) {
        this.testGroupName = testGroupName
        this.repository = repository
    }

    public String getParamName() {
        return "${Utils.safeVariableNameUpperCase(this.repository.name)}_${Utils.safeVariableNameUpperCase(this.testGroupName)}"
    }

    public Repository modifiedRepository() {
        Repository repository = this.repository.clone()
        repository.envName = this.paramName
        repository.directory = "${Utils.safeVariableNameLowerCase(testGroupName)}/${repository.directory}"
        repository.allowTags = false
        repository.allowNotifyCommit = false
        return repository
    }
}
