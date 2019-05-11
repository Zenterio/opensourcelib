package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

class ReleasePackagingBuildStepScriptlet extends BuildStepScriptlet {

    public ReleasePackagingBuildStepScriptlet(IScriptlet template,
                                              String projectName,
                                              String originName) {
        super(template, '${PRODUCT}', 0)
        this.addMacroDefinitions(tokenizeAndEscape('PROJECT', projectName))
        this.addMacroDefinitions(tokenizeAndEscape('ORIGIN', originName))
    }
}
