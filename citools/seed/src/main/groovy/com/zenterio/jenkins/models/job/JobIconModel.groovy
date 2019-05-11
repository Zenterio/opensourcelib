package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.JobIcon


class JobIconModel extends ModelProperty {

    final String iconFile

    public JobIconModel(JobIcon jobIcon) {
        this.iconFile = jobIcon.getIcon()
    }

}
