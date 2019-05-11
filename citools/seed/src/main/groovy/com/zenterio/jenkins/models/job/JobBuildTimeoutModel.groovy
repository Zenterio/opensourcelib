package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.configuration.BuildTimeout
import com.zenterio.jenkins.configuration.BuildTimeoutPolicy
import com.zenterio.jenkins.models.ModelProperty

class JobBuildTimeoutModel extends ModelProperty {

    public final static String TIME_OUT_VARIABLE =  'BUILD_TIMEOUT'

    public BuildTimeoutPolicy policy
    public Boolean failBuild
    public Integer minutes
    public Boolean configurable
    public String description

    public int elasticTimeOvershoot = 400
    public int elasticMinBuilds = 3

    public JobBuildTimeoutModel(BuildTimeout buildTimeout) {
        this(buildTimeout.policy, buildTimeout.minutes, buildTimeout.failBuild, buildTimeout.configurable)
    }

    JobBuildTimeoutModel(BuildTimeoutPolicy policy, Integer minutes, Boolean failBuild, Boolean configurable) {
        super()
        this.policy = policy
        this.failBuild = failBuild
        this.minutes = minutes
        this.configurable = configurable
        this.description = getDescription(policy, configurable)
    }

    protected String getDescription(BuildTimeoutPolicy policy, Boolean configurable) {
        String extra = ''
        if (configurable) {
            extra = ' after configured period of time'
        }
        return "Build timeout policy '${policy.name}' aborted the build${extra}."
    }
}
