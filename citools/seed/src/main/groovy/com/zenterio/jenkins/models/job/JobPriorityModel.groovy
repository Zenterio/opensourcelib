package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.Priority
import com.zenterio.jenkins.models.ModelProperty

class JobPriorityModel extends ModelProperty {

    final Priority priority

    JobPriorityModel(Priority priority) {
        super()
        this.priority = priority
    }
}
