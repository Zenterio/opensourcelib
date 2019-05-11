package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon

/**
 * Generates a groovy scripts for generating sign jenkins-action.
 */
class AnnotateBuildChainPingBackScriptlet extends TemplateScriptlet {

    public AnnotateBuildChainPingBackScriptlet(IScriptlet template) {
        super(template)
        this.addMacroDefinitions([
            '#ICON#': JobIcon.ANNOTATE.getPath(),
            ])
    }
}
