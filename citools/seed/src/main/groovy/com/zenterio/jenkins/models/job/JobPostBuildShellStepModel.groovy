package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.scriptlet.IScriptlet


class JobPostBuildShellStepModel extends JobBuildStepModel {

    public JobPostBuildShellStepModel(String script) {
        super(script)
    }

    public JobPostBuildShellStepModel(IScriptlet scriptlet) {
        super(scriptlet)
    }

}
