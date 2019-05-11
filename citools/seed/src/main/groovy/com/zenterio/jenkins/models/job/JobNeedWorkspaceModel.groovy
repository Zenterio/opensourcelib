package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobNeedWorkspaceModel extends ModelProperty {

    public Boolean needed

    public JobNeedWorkspaceModel(Boolean needed) {
        super()
        this.needed = needed
    }
}
