package com.zenterio.jenkins.models.job

import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty


/**
 * Copies artifacts from a given build based on build-number.
 */
class JobCopyArtifactsFromBuildNumberModel extends ModelProperty {

    /**
     * Parent job for the build that should be copied from.
     */
    public JobModel parentJob

    /**
     * Alternative way of specifying which job to copy from.
     * If set, that will be used. Use alternative constructor.
     */
    final private String jobName

    /**
     * Build number of the build that should be copied from.
     */
    public String buildNumber

    /**
     * Pattern for which artifacts should be copied.
     */
    public String includeGlob

    /**
     * Directory relative workspace where the artifacts will be copied to.
     */
    public String targetPath

    /**
     * Set to true if the copied file structure should be flattened.
     */
    public Boolean flattenFiles

    /**
     *
     * @param parentJob     The job to copy from; if set to null, the model will
     *                      discover the parent name by itself by looking for
     *                      the model parent-parent's jobName.
     * @param buildNumber   The build number to copy from. Can be a string with
     *                      build parameter in the form ${VARNAME}
     * @param includeGlob   The file patterns to match for copy; if left blank,
     *                      all files will be copied.
     * @param targetPath    The directory where the files should be copied to,
     *                      relative to workspace; if left blank, the workspace
     *                      root will be used.
     * @param flattenFiles  Will flatten the file list if set to true; default
     *                      is false.
     */
    public JobCopyArtifactsFromBuildNumberModel(JobModel parentJob, String buildNumber,
            String includeGlob = "", String targetPath = "", Boolean flattenFiles = false) {
        super()
        this.parentJob = parentJob
        this.jobName = null
        this.buildNumber = buildNumber
        this.includeGlob = includeGlob
        this.targetPath = targetPath
        this.flattenFiles = flattenFiles
    }

    /**
     *
     * @param jobName       The name of the job to copy from.Can be a string with
     *                      build parameter in the form ${VARNAME}
     * @param buildNumber   The build number to copy from. Can be a string with
     *                      build parameter in the form ${VARNAME}
     * @param includeGlob   The file patterns to match for copy; if left blank,
     *                      all files will be copied.
     * @param targetPath    The directory where the files should be copied to,
     *                      relative to workspace; if left blank, the workspace
     *                      root will be used.
     * @param flattenFiles  Will flatten the file list if set to true; default
     *                      is false.
     */
    public JobCopyArtifactsFromBuildNumberModel(String jobName, String buildNumber,
            String includeGlob = "", String targetPath = "", Boolean flattenFiles = false) {
        super()
        this.jobName = jobName
        this.parentJob = null
        this.buildNumber = buildNumber
        this.includeGlob = includeGlob
        this.targetPath = targetPath
        this.flattenFiles = flattenFiles
    }


    /**
     *
     * @return the name of the job that should be copied from.
     */
    public String getJobName() {
        if (this.jobName) {
            return this.jobName
        }
        
        JobNameModel jn
        if (this.parentJob) {
            jn = this.parentJob.getProperty(JobNameModel)
        } else {
            ModelEntity entity = this.getParent(JobModel, false).getParent(JobModel, false)
            jn = entity.getProperty(JobNameModel)
        }
        return jn.name
    }
}
