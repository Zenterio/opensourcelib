package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * Generates a groovy scripts for generating sign jenkins-action.
 */
class PromoteBuildChainPingBackScriptlet extends TemplateScriptlet {

    public PromoteBuildChainPingBackScriptlet(IScriptlet template) {
        super(template)
        this.addMacroDefinitions([
                (groovyToken('ICON')): escape(JobIcon.PROMOTION.getPath()),
            ])
    }
}
