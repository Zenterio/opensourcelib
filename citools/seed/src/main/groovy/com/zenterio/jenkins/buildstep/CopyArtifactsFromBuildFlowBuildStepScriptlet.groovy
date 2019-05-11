package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class CopyArtifactsFromBuildFlowBuildStepScriptlet extends TemplateScriptlet {

    CopyArtifactsFromBuildFlowBuildStepScriptlet(IScriptlet template,
                                                    String topJobName,
                                                    String topBuildNumber,
                                                    String baseDir) {
        super(template)
        this.addMacroDefinitions([
                (groovyToken("TOP_JOB_NAME")): escape(topJobName),
                (groovyToken("TOP_BUILD_NUMBER")): escape(topBuildNumber),
                (groovyToken("BASE_DIR")): escape(baseDir)
        ])
    }
}
