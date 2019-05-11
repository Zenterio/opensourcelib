package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class GenerateChangelogScriptlet extends TemplateScriptlet {

    public GenerateChangelogScriptlet(IScriptlet template,
                                      String repositories,
                                      String current,
                                      String previous) {
        super(template)
        this.addMacroDefinitions([
                (token('REPOSITORIES')): escape(repositories),
                (token('CURRENT_RELEASE')): escape(current),
                (token('PREVIOUS_RELEASE')): escape(previous)
            ])
    }
}