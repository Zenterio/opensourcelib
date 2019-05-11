package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty

class JobScmTriggerModel extends ModelProperty {

    String cronString

    public JobScmTriggerModel(String cronString) {
        super()
        this.cronString = cronString
    }
}
