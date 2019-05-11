package com.zenterio.jenkins.appliers

import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.configuration.ConcurrentBuilds
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.job.JobBuildTimeoutModel
import com.zenterio.jenkins.models.job.JobBuildTimeoutParameterModel
import com.zenterio.jenkins.models.job.JobExecuteConcurrentBuildModel

class ConcurrentBuildsApplier {

    public static void apply(ConcurrentBuilds concurrentBuilds, IModel job) {
        if (concurrentBuilds.enabled) {
            job << new JobExecuteConcurrentBuildModel(true)
        }
    }
}
