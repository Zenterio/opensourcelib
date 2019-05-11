package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.ModelProperty

/**
 * Abstract base class for creating custom build flow DSL parameters.
 * Create a sub class with special behavior that returns a value
 * customized to its purpose.
 */
abstract class JobBuildFlowDslParameterModel extends ModelProperty {

    String parameterName

    public JobBuildFlowDslParameterModel(String parameterName) {
        this.parameterName = parameterName;
    }

    abstract public String getParameterValue()
}
