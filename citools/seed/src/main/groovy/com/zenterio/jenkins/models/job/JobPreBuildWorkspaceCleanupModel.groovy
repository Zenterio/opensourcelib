package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobPreBuildWorkspaceCleanupModel extends ModelProperty {
    protected String excludePattern

    JobPreBuildWorkspaceCleanupModel(String excluded=null) {
        super()
        this.excludePattern = excluded
    }
}
