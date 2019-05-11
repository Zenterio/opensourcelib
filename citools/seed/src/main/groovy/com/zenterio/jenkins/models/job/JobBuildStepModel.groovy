package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.scriptlet.IScriptlet


class JobBuildStepModel extends ModelProperty {

    String script

    public JobBuildStepModel(String script) {
        super()
        this.script = script
    }

    public JobBuildStepModel(IScriptlet scriptlet) {
        super()
        this.script = scriptlet.getContent()
    }

}
