package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.ModelProperty

/**
 * A model that has this property, will not be called with parameter.
 */
class JobBuildFlowDslExcludeParameterModel extends ModelProperty {

    String parameterToExclude

    public JobBuildFlowDslExcludeParameterModel(String parameterToExclude) {
        this.parameterToExclude = parameterToExclude
    }

}
