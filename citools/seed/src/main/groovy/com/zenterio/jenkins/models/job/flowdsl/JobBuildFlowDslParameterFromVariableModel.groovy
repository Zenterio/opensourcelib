package com.zenterio.jenkins.models.job.flowdsl

import com.zenterio.jenkins.models.IPropertySelector
import com.zenterio.jenkins.models.job.JobNameModel

import static com.zenterio.jenkins.Utils.safeVariableName

/**
 * Attach an instance of this class to a job model included in a DSL flow,
 * and the variable in the flow will be passed as a parameter
 * to the job model.
 */
class JobBuildFlowDslParameterFromVariableModel extends JobBuildFlowDslParameterModel {

    String parameterValue

    /**
     * The DSL will call the job with the specified parameter name and parameter value.
     * Default is to use the parameter name as the value which is useful when the job
     * uses the same parameter names as the flow.
     * @param parameterName Parameter name
     * @param parameterValue Parameter value, default the same as the parameterName
     */
    public JobBuildFlowDslParameterFromVariableModel(String parameterName, String parameterValue=null) {
        super(parameterName)
        this.parameterValue = parameterValue
    }

    public String getParameterValue() {
        if (this.parameterValue == null) {
            return this.parameterName
        } else {
            return this.parameterValue
        }
    }
}
