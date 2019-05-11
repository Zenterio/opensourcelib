package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * General purpose scriptlet for Summary actions.
 * Changes #ICON# to icon path.
 * Changes #JOB_NAME# to the name of the jenkins job that performs the build action.
 */
class SummaryActionScriptlet extends TemplateScriptlet {

    public SummaryActionScriptlet(IScriptlet template, String jobName, JobIcon icon) {
        super(template)

        this.addMacroDefinitions([
            (groovyToken("JOB-NAME")): escape(jobName),
            (groovyToken("ICON")): escape(icon.path),
        ])
    }
}
