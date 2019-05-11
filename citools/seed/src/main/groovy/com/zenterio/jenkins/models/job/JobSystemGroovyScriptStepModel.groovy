package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.scriptlet.IScriptlet

class JobSystemGroovyScriptStepModel extends JobBuildStepModel {

    public JobSystemGroovyScriptStepModel(String script) {
        super(script)
    }

    public JobSystemGroovyScriptStepModel(IScriptlet scriptlet) {
        super(scriptlet)
    }
}
