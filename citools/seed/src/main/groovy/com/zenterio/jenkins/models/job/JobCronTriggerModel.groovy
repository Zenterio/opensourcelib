package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty


class JobCronTriggerModel extends ModelProperty {

    String cronString

    public JobCronTriggerModel(String cronString) {
        super()
        this.cronString = cronString
    }
}
