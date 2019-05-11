package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.builders.GroovyStatementBuilder.curlify
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class AnnotateBuildChainBuildStepScriptlet extends TemplateScriptlet {

    AnnotateBuildChainBuildStepScriptlet(IScriptlet template,
                                         String topJobName=curlify('build.buildVariableResolver.resolve("top_job_name")'),
                                         String topBuildNumber=curlify('build.buildVariableResolver.resolve("top_build_number")')) {
        super(template)
        this.addMacroDefinitions([
                (groovyToken("TOP_JOB_NAME")): escape(topJobName),
                (groovyToken("TOP_BUILD_NUMBER")): escape(topBuildNumber)
        ])
    }
}
