/**
 * Auto-generated script from template CoverityRunIfChanges.groovy (Seed scriptlet)
 *      Repo-var-name-map: #REPO_VAR_NAME_MAP#
 *      Repo-default-branch-map: #REPO_DEFAULT_BRANCH_MAP#
 * Checks if there has been new debug builds since last coverity, aborts build if not.
 *
 */
import hudson.model.*

import java.util.regex.Matcher

{ it ->

    Map repoVarNameMap = evaluate("#REPO_VAR_NAME_MAP#")
    Map repoDefaultBranchMap = evaluate("#REPO_DEFAULT_BRANCH_MAP#")
    String debugBuildInfo
    String coverityBuildInfo

    Closure setGitParameters = { String buildInfo, Map varNames, Map defaultBranches ->
        varNames.each { repo, environmentVariable ->
            String value
            if (buildInfo) {
                Matcher commit = buildInfo =~ /(?s)Repository: ${repo}.*?Commit: (.*?)\n/
                value = commit[0][1]
            } else {
                value = defaultBranches[repo]
            }
            ParameterValue param = new StringParameterValue(environmentVariable, value)
            ParametersAction pa = new ParametersAction(param)
            build.addAction(pa)
        }
    }

    try {
        debugBuildInfo = build.getParent().getWorkspace().child("${build.workspace.getRemote()}/source/debug/result/build-info.txt").readToString()
    } catch (IOException e) {
        println("No previous build, building latest")
        setGitParameters(null, repoVarNameMap, repoDefaultBranchMap)
        return
    }
    try {
        coverityBuildInfo = build.getParent().getWorkspace().child("${build.workspace.getRemote()}/source/coverity/result/build-info.txt").readToString()
    } catch (IOException e) {
        println("No previous coverity, building same as latest debug")
        setGitParameters(debugBuildInfo, repoVarNameMap, repoDefaultBranchMap)
        return
    }
    int debugOriginIndex = debugBuildInfo.indexOf("Origin")
    int coverityOriginIndex = coverityBuildInfo.indexOf("Origin")
    if ( debugBuildInfo[debugOriginIndex..-1] == coverityBuildInfo[coverityOriginIndex..-1] ) {
        println("Build interrupted due to no changes")
        build.doStop()
        return
    } else {
        println("Latest coverity does not match latest debug, building latest debug")
        setGitParameters(debugBuildInfo, repoVarNameMap, repoDefaultBranchMap)
    }
}();
