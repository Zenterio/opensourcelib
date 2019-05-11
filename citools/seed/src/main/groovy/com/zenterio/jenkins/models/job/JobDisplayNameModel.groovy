package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobDisplayNameModel extends ModelProperty {
    public String displayName

    public JobDisplayNameModel(String displayName) {
        super()
        this.displayName = displayName
    }
}
