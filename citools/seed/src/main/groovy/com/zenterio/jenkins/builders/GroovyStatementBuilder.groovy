package com.zenterio.jenkins.builders

class GroovyStatementBuilder {

    public static String quotify(String string) {
        return "\"${string}\""
    }

    public static String curlify(String string) {
        return "\${${string}}"
    }

    public static String getBuild(String jobName, String buildNumber) {
        return "jenkins.model.Jenkins.getInstance().getJob(${jobName}).getBuildByNumber(${buildNumber})"
    }

    public static String getBuild(Boolean postBuildScript) {
        if (postBuildScript) {
            return "manager.build"
        } else {
            return "build"
        }
    }

    public static String getParameterFromBuild(String build, String parameter) {
        return "${build}.buildVariableResolver.resolve(${quotify(parameter)})"
    }

    public static String getIntParameterFromBuild(String build, String parameter) {
        return getParameterFromBuild(build, parameter) + '.toInteger()'
    }

    public static String getCurrentBuildParameter(String parameter, Boolean postBuildScript=false) {
        return getParameterFromBuild(getBuild(postBuildScript), parameter)
    }

    public static String getCurrentBuildIntParameter(String parameter, Boolean postBuildScript=false) {
        return getIntParameterFromBuild(getBuild(postBuildScript), parameter)
    }
}
