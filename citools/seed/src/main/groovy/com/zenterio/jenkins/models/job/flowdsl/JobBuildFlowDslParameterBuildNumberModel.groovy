package com.zenterio.jenkins.models.job.flowdsl

import static com.zenterio.jenkins.Utils.safeVariableName

import com.zenterio.jenkins.models.IPropertySelector
import com.zenterio.jenkins.models.job.JobModel
import com.zenterio.jenkins.models.job.JobNameModel

/**
 * Attach an instance of this class to a job model included in a DSL flow,
 * and the build-number of the model's parent will be passed as a parameter
 * to the job model.
 * <p>
 * The build-number will be passed as argument to the parameter named as
 * specified in the constructor when instantiating this class.
 */
class JobBuildFlowDslParameterBuildNumberModel extends JobBuildFlowDslParameterModel {

    /**
     * Optional property. If used, that job will be selected as parent instead
     * of the auto-discovery mechanism based on model relationships.
     */
    JobModel parentJob

    /**
     * The specified parameter name will be passed the value of the
     * parents build number.
     * @param parameterName     Parameter name
     * @param parentJob         Parent job if different from the models parent.
     */
    public JobBuildFlowDslParameterBuildNumberModel(String parameterName, JobModel parentJob=null) {
        super(parameterName)
        this.parentJob = parentJob
    }

    public String getParameterValue() {
        IPropertySelector parent

        if (this.parentJob) {
            parent = this.parentJob
        } else {
            /*
             * Find parent which is the flow job, that is the parent with
             * a job flow DSL step model.
             * For that parent, get the DSL step model to get access to
             * the jobPassFilter, it is the class that the DSL step model
             * use to find which entities to include in the graph.
             */
            Class jobPassFilter = ((FlowJobFlowDslStepModel)this.getParentProperty(FlowJobFlowDslStepModel)).jobPassFilter

            /*
             * Using the jobPassFilter class, find the closest parent (not including
             * the entity itself) that match, hence the direct parent in the graph.
             */
            parent = this.getParents(jobPassFilter, false)[1]

            if (!parent) {
                throw new RuntimeException("JobBuildFlowDslParameterBuildNumberModel can only be placed on a job model with a parent.")
            }
        }

        /*
         * Get the parents name
         */
        String parentName = safeVariableName(parent[JobNameModel]?.name)

        /* create parameter command string */
        return "build_${parentName}.build.number"
    }
}
