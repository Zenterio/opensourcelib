package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.scriptlet.IScriptlet


class JobPostBuildScriptWrapperModel extends ModelProperty {

    Boolean buildOnFailure
    Boolean buildOnSuccess
    Boolean markUnstableOnFailure

    public JobPostBuildScriptWrapperModel(Boolean buildOnSuccess, Boolean buildOnFailure, Boolean markUnstableOnFailure) {
        super()
        this.buildOnFailure = buildOnFailure
        this.buildOnSuccess = buildOnSuccess
        this.markUnstableOnFailure = markUnstableOnFailure
    }
}
