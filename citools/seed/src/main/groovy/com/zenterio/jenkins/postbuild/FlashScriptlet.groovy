package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.JobIcon
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * Generates a groovy scripts for annotate build chain jenkins-action.
 * Changes #ICON# to a list of repositories.
 * Changes #ANNOTATE_JOB_NAME# to the name of the jenkins job that performs the
 * build promotion. Allows for use of different annotation build jobs across projects.
 */
class FlashScriptlet extends TemplateScriptlet {

    public FlashScriptlet(IScriptlet template, String flashJobName) {
        super(template)

        this.addMacroDefinitions([
                (groovyToken("FLASH_JOB_NAME")): escape(flashJobName),
                (groovyToken("ICON")): escape(JobIcon.FLASH.getPath()),
            ])
    }
}
