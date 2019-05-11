package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.configuration.Repository

class JobGitScmModel extends ModelProperty {

    Repository[] repositories
    Boolean acceptNotifyCommit

    public JobGitScmModel(Repository[] repositories, acceptNotifyCommit) {
        this.repositories = repositories
        this.acceptNotifyCommit = acceptNotifyCommit
    }

}
