package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobLabelModel extends ModelProperty {

    String label
    Boolean configurable

    public JobLabelModel(String label, Boolean configurable = false) {
        super()
        this.label = label
        this.configurable = configurable
    }

}
