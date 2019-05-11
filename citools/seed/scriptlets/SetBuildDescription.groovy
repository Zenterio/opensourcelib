/**
 * Auto-generated script from template SetBuildDescription.groovy
 *
 * MACRO:
 * jobName     = #JOB_NAME#
 * buildNumber = #BUILD_NUMBER#
 * description  = #DESCRIPTION#
 *
 * @Summary
 * This script is used to set the description of a jenkins build
 *
 */

{it ->
    String jobName = "#JOB_NAME#"
    String buildNumber = "#BUILD_NUMBER#"
    String description = "#DESCRIPTION#"

    def targetJob = jenkins.model.Jenkins.instance.getJob(jobName)
    def targetBuild = targetJob.getBuildByNumber(buildNumber.toInteger())

    println("Setting description of ${jobName}")
    targetBuild.setDescription(description)
}();
