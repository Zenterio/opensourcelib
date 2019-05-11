package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty;
import com.zenterio.jenkins.scriptlet.IScriptlet;

class JobGroovyPostBuildModel extends ModelProperty {

    private String script;

    public JobGroovyPostBuildModel(String script) {
        super();
        this.script = script;
    }

    public JobGroovyPostBuildModel(IScriptlet scriptlet) {
        super();
        this.script = scriptlet.getContent();
    }

    public getScript() {
        return this.script;
    }

}
