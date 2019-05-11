package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelProperty
import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
@AutoClone
class JobLogSizeCheckerModel extends ModelProperty {

    final Boolean failBuild
    final int maxSize

    public JobLogSizeCheckerModel(int maxSizeInMB, Boolean failBuild) throws IllegalArgumentException {
        super()
        this.failBuild = failBuild
        this.maxSize = maxSizeInMB
    }
}
