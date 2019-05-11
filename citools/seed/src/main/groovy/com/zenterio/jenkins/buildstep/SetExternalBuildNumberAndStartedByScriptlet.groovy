package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.StartedBy
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class SetExternalBuildNumberAndStartedByScriptlet extends TemplateScriptlet {

    public SetExternalBuildNumberAndStartedByScriptlet(IScriptlet template, StartedBy startedBy, Boolean extBuildNumberSameAsBuildNumber) {
        super(template)

        this.addMacroDefinitions([
                (groovyToken("SET_STARTED_BY")): escape(startedBy.toString())
        ])

        if (extBuildNumberSameAsBuildNumber) {
            this.addMacroDefinitions([
                (groovyToken("EXT_BUILD_NUMBER")): escape('${build.getNumber()}')
            ])
        } else {
            this.addMacroDefinitions([
                (groovyToken("EXT_BUILD_NUMBER")): escape('${build.getEnvironment(listener)["external_build_number"]}')
            ])
        }

    }
}
