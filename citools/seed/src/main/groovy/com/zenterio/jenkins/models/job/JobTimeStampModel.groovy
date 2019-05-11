package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobTimeStampModel extends ModelProperty {

    Boolean enabled

    public JobTimeStampModel(Boolean enabled = true) {
        super()
        this.enabled = enabled
    }
}
