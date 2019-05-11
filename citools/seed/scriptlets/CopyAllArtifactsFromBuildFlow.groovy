/**
 * Auto-generated script from template CopyAllArtifactsFromBuildFlow.groovy
 *
 * topJobName: #TOP_JOB_NAME#
 * topBuildNumber: #TOP_BUILD_NUMBER#
 * baseDir: #BASE_DIR#
 *
 */

import hudson.plugins.copyartifact.SpecificBuildSelector
import hudson.plugins.copyartifact.CopyArtifact
import hudson.FilePath


def copyAllArtifactsFromBuild(buildName, buildNumber, target) {

    // Doc: https://github.com/jenkinsci/copyartifact-plugin/blob/master/src/main/java/hudson/plugins/copyartifact/CopyArtifact.java
    CopyArtifact copyArtifact = new CopyArtifact(buildName)

    copyArtifact.setSelector(new SpecificBuildSelector(buildNumber.toString()))
    copyArtifact.setOptional(false)
    copyArtifact.setTarget(target)
    copyArtifact.setFilter(null)
    copyArtifact.setFlatten(false)
    copyArtifact.setFingerprintArtifacts(false)

    // "build" is a global jenkins variable
    // "launcher" is a global jenkins variable
    // "listener" is a global jenkins variable
    copyArtifact.perform(build, build.workspace, launcher, listener)
}

def copyConsoleLogFromBuild(srcBuild, targetFilePath) {
    FilePath dest
    String targetWorkspacePath = build.workspace.toString() + "/${targetFilePath}"
    if(build.workspace.isRemote())
    {
        channel = build.workspace.channel
        dest = new FilePath(channel, targetWorkspacePath)
    } else {
        dest = new FilePath(new File(targetWorkspacePath))
    }
    outputStream = null
    try {
        outputStream = dest.write()
        srcBuild.writeWholeLogTo(outputStream)
    } finally {
        if (outputStream != null) {
            outputStream.flush()
            outputStream.close()
        }
    }
}

def hasArtifacts(build) {
    return build.getArtifacts().size() > 0
}

def doCopy(declarer, baseDir, topBuild) {
    def downstreamBuilds = declarer.getDownStream(topBuild)
    downstreamBuilds.each { downstreamBuild ->
        if (downstreamBuild != null) {
            copyFromAllDownstreamBuilds(downstreamBuild, baseDir)
            if (hasArtifacts(downstreamBuild)) {
                String projectDir = "${baseDir}/${downstreamBuild.project.name}"
                copyAllArtifactsFromBuild(downstreamBuild.project.name, downstreamBuild.number, projectDir)
                copyConsoleLogFromBuild(downstreamBuild, "${projectDir}/consoleText.txt")
            }
        }
    }
}

def copyFromAllDownstreamBuilds(topBuild, baseDir) {
    if (jenkins.model.Jenkins.getInstance().getPlugin("build-flow-plugin") != null) {
        def declarer = new org.jenkinsci.plugins.buildgraphview.FlowDownStreamRunDeclarer()
        doCopy(declarer, baseDir, topBuild)
    }

    org.jenkinsci.plugins.buildgraphview.DownStreamRunDeclarer.all().each { declarer ->
        doCopy(declarer, baseDir, topBuild)
    }
}

{ it ->
    String topJobName = "#TOP_JOB_NAME#"
    String topBuildNumber = "#TOP_BUILD_NUMBER#"
    String baseDir = "#BASE_DIR#"

    def topJob = jenkins.model.Jenkins.instance.getJob(topJobName)
    def topBuild = topJob.getBuildByNumber(topBuildNumber.toInteger())

    copyFromAllDownstreamBuilds(topBuild, baseDir)
}();

return
