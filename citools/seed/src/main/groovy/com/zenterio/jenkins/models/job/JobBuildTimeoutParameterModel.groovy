package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.BuildTimeoutPolicy

class JobBuildTimeoutParameterModel extends JobParameterModel {

    JobBuildTimeoutParameterModel(String name, JobBuildTimeoutModel model) {
        super(name, getDefaultValue(model), getDescription(model))
    }

    protected static String getDescription(JobBuildTimeoutModel model) {
        switch (model.policy) {
            case BuildTimeoutPolicy.ABSOLUTE:
                return 'The job timeout in minutes (at least 3).'
            case BuildTimeoutPolicy.ELASTIC:
                return "The default job timeout if less than ${model.elasticMinBuilds} build is present to calculate an elastic timeout from."
            default:
                return ''
        }
    }

    protected static String getDefaultValue(JobBuildTimeoutModel model) {
        switch (model.policy) {
            case BuildTimeoutPolicy.ABSOLUTE:
            case BuildTimeoutPolicy.ELASTIC:
                return Integer.toString(model.minutes)
            default:
                return ''
        }
    }
}
