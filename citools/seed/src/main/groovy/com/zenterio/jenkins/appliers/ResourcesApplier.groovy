package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.Resources
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobResourcesModel

class ResourcesApplier {

    public static void apply(Resources resources, IModel job) {
        if (resources.enabled) {
            job << new JobResourcesModel(resources)
        }
    }
}
