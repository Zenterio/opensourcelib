/**
 * Auto-generated script from template AnnotateBuildChain.groovy
 *
 * topJobName: #TOP_JOB_NAME#
 * topBuildNumber: #TOP_BUILD_NUMBER#
 *
 * @Summary
 * This script annotates a build chain with the description from the
 * top build.
 *
 * It is a system groovy script build step.
 *
 * Environment variables/job arguments used:
 * top_job_name : Name of job to propagate information from
 * top_build_number : Number of the build.
 *
 */


/**
 * Log affected builds and any previous annotations.
 *
 * @param build   A Jenkins build object.
 */
def logAnnotationToConsole(build) {
    def oldAnnotation = build.getDescription()
    println(build.getFullDisplayName())
    if (oldAnnotation != null) {
        println("Replaced old Annotation:")
        println(oldAnnotation)
    }
    println("-----")
}

def doAnnotations(declarer, build, newAnnotation) {
    downstreamBuilds = declarer.getDownStream(build)
    downstreamBuilds.each { downstreamBuild ->
        if (downstreamBuild != null) {
            logAnnotationToConsole(downstreamBuild)
            downstreamBuild.setDescription(newAnnotation)
            setAnnotationAndRecurse(downstreamBuild, newAnnotation)
        }
    }
}


/**
 * Change annotation for a build
 *
 * param build      A Jenkins build object.
 * param annotation New annotation
 */
def setAnnotationAndRecurse(build, newAnnotation) {
    if (jenkins.model.Jenkins.getInstance().getPlugin("build-flow-plugin") != null) {
        def declarer = new org.jenkinsci.plugins.buildgraphview.FlowDownStreamRunDeclarer()
        doAnnotations(declarer, build, newAnnotation)
    }

    org.jenkinsci.plugins.buildgraphview.DownStreamRunDeclarer.all().each { declarer ->
        doAnnotations(declarer, build, newAnnotation)
    }
}

// logic wrapped in closure to avoid polluting global scope
{ it ->
    String topJobName = "#TOP_JOB_NAME#"
    String topBuildNumber = "#TOP_BUILD_NUMBER#"

    def topJob = jenkins.model.Jenkins.instance.getJob(topJobName)
    def topBuild = topJob.getBuildByNumber(topBuildNumber.toInteger())
    def topDescription = topBuild.getDescription()

    println("-----")
    println("Propagating annotation for ${topBuild.getFullDisplayName()}")
    println(topDescription)
    println("-----")
    setAnnotationAndRecurse(topBuild, topDescription)
    return
}();
