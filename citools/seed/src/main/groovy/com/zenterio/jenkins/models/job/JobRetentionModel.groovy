package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.RetentionPolicy

class JobRetentionModel extends ModelProperty {

    public RetentionPolicy policy

    public JobRetentionModel(RetentionPolicy policy) {
        super()
        this.policy = policy
    }
}
