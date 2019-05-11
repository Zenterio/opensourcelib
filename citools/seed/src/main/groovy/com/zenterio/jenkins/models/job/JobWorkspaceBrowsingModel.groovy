package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobWorkspaceBrowsingModel extends ModelProperty{

    public Boolean enabled

    public JobWorkspaceBrowsingModel(Boolean enabled){
        super()
        this.enabled = enabled
    }
}
