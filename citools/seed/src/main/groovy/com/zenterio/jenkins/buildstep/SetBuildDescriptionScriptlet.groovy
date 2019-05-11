package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class SetBuildDescriptionScriptlet extends TemplateScriptlet {

    SetBuildDescriptionScriptlet(IScriptlet template,
                                 String jobName,
                                 String buildNumber,
                                 String description) {
        super(template)
        this.addMacroDefinitions([
                (groovyToken("JOB_NAME")): escape(jobName),
                (groovyToken("BUILD_NUMBER")): escape(buildNumber),
                (groovyToken("DESCRIPTION")): escape(description)
        ])
    }
}
