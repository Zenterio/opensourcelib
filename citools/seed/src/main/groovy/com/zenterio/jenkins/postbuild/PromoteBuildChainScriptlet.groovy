package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.JobIcon
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * Generates a groovy scripts for promote build chain jenkins-action.
 * Changes #ICON# to a list of repositories.
 * Changes #PROMOTE_JOB_NAME# to the name of the jenkins job that performs the
 * build promotion. Allows for use of different promotion build jobs across projects.
 */
class PromoteBuildChainScriptlet extends TemplateScriptlet {

    public PromoteBuildChainScriptlet(IScriptlet template, String promoteBuildJobName) {
        super(template)

        this.addMacroDefinitions([
                (groovyToken("PROMOTE_JOB_NAME")): escape(promoteBuildJobName),
                (groovyToken("ICON")): escape(JobIcon.PROMOTION.path),
            ])
    }
}
