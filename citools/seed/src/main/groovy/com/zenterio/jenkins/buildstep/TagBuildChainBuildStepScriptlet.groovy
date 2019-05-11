package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class TagBuildChainBuildStepScriptlet extends TemplateScriptlet {

    public TagBuildChainBuildStepScriptlet(IScriptlet template,
                                           String repositories,
                                           String tagName,
                                           String sourceTag) {
        super(template)
        this.addMacroDefinitions([
                (token('REPOSITORIES')): escape(repositories),
                (token('TAG_NAME')): escape(tagName),
                (token('SOURCE_TAG')): escape(sourceTag)
            ])
    }
}
