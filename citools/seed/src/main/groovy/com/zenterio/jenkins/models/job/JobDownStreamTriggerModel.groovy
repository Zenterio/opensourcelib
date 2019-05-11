package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.BaseModel
import com.zenterio.jenkins.scriptlet.IScriptlet


class JobDownStreamTriggerModel extends ModelProperty {

    DownStreamTriggerParameter[] parameters
    boolean block

    public JobDownStreamTriggerModel(DownStreamTriggerParameter[] parameters, boolean block) {
        this.parameters = parameters
        this.block = block
    }
}
