package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.builders.GroovyStatementBuilder.curlify
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class PromoteBuildChainBuildStepScriptlet extends TemplateScriptlet {

    PromoteBuildChainBuildStepScriptlet(IScriptlet template,
                                        String topJobName,
                                        String topBuildNumber,
                                        String topPromotionLevel=curlify('topPromoteAction.getLevelValue()')) {
        super(template)
        this.addMacroDefinitions([
                (groovyToken("TOP_JOB_NAME")): escape(topJobName),
                (groovyToken("TOP_BUILD_NUMBER")): escape(topBuildNumber),
                (groovyToken("PROMOTE_LEVEL")): escape(topPromotionLevel),
        ])
    }
}
