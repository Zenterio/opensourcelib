package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.AutoCloneStyle
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone(style=AutoCloneStyle.COPY_CONSTRUCTOR)
class BuildTimeout extends BaseConfig {

    /**
     * Enabled
     */
    final Boolean enabled

    /**
     * Timeout policy
     */
    final BuildTimeoutPolicy policy

    /**
     * Timeout in minutes, used for all policies except disabled
     */
    final Integer minutes

    /**
     * True: fail build on timeout
     * False: abort build on timeout
     */
    final Boolean failBuild

    /**
     * Allow setting BUILD_TIMEOUT as a job configuration option
     */
    final Boolean configurable

    BuildTimeout(BuildTimeoutPolicy policy=null, Integer minutes=null, Boolean failBuild=false, Boolean configurable=false, Boolean enabled=true) {

        if (enabled) {
            if(minutes == null) {
                throw new IllegalArgumentException("The minutes argument of a BuildTimeout can not be null if enabled is true.")
            }
            if (minutes <= 0) {
                throw new IllegalArgumentException("The minutes argument of a BuildTimeout has to be greater than 0 if enabled is true.")
            }
            if (policy == BuildTimeoutPolicy.ABSOLUTE && minutes < 3) {
                throw new IllegalArgumentException("If the BuildTimeoutPolicy is set to ABSOLUTE, the minutes argument has to be at least 3, if enabled is true.")
            }
            if (policy == null) {
                throw new IllegalArgumentException("The policy of a BuildTimeout has to have a value if enabled is true.")
            }
        }

        this.policy = policy
        this.minutes = minutes
        this.failBuild = failBuild
        this.configurable = configurable
        this.enabled = enabled

    }

    public static BuildTimeout getTestData() {
        BuildTimeout data = new BuildTimeout(BuildTimeoutPolicy.ABSOLUTE, 3, false, false, true)
        return data
    }

}
