package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.scriptlet.IScriptlet


class JobShellStepModel extends JobBuildStepModel {

    public JobShellStepModel(String script) {
        super(script)
    }

    public JobShellStepModel(IScriptlet scriptlet) {
        super(scriptlet)
    }
}
