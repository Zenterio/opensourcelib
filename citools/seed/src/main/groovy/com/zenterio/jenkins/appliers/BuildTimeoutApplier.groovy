package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobBuildTimeoutModel
import com.zenterio.jenkins.models.job.JobBuildTimeoutParameterModel

class BuildTimeoutApplier {

    public static void apply(BuildTimeout buildTimeout, IModel job) {
        if (buildTimeout.enabled) {
            JobBuildTimeoutModel model = new JobBuildTimeoutModel(buildTimeout)
            if (model.configurable) {
                job << new JobBuildTimeoutParameterModel(JobBuildTimeoutModel.TIME_OUT_VARIABLE, model)
            }
            job << model
        }
    }
}
