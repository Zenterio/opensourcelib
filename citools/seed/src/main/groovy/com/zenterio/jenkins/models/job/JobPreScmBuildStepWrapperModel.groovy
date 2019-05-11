package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobPreScmBuildStepWrapperModel extends ModelProperty {

    private boolean failOnError

    public JobPreScmBuildStepWrapperModel(Boolean failOnError) {
        this.failOnError = failOnError
    }
}
