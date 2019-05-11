package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobExecuteConcurrentBuildModel extends ModelProperty {

    final boolean allowConcurrentBuild

    public JobExecuteConcurrentBuildModel(boolean allowConcurrentBuild) {
        super()
        this.allowConcurrentBuild = allowConcurrentBuild
    }

}
