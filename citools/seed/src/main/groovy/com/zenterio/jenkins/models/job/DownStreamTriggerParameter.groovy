package com.zenterio.jenkins.models.job


class DownStreamTriggerParameter {

    String jobName
    String condition
    Boolean currentBuild
    String propertiesFile
    String nodeLabel

    /**
     * Triggers the downstream job with parameters from the propertiesFile
     * @param jobName             The name of the job to trigger
     * @param condition           Describes when the job should be triggered
     * @param propertiesFile      The file with parameters
     */
    public DownStreamTriggerParameter(String jobName, String condition,
                                      String propertiesFile) {
        this.jobName = jobName
        this.condition = condition
        this.propertiesFile = propertiesFile
        this.currentBuild = false
        this.nodeLabel = null
    }

    /**
     * Triggers the downstream job with the same parameters as the current build
     * @param jobName        The name of the job to trigger
     * @param condition      Describes when the job should be triggered
     * @param nodeLabel      The node to trigger the job on. This is needed because
     *                       currentBuild true will otherwise trigger with the same node
     *                       as the parent job
     */
    public DownStreamTriggerParameter(String jobName, String condition, JobLabelModel nodeLabel) {
        this.jobName = jobName
        this.condition = condition
        this.propertiesFile = null
        this.currentBuild = true
        this.nodeLabel = nodeLabel.label
    }

}
