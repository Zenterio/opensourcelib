package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.token

class FlashBuildStepScriptlet extends TemplateScriptlet {

    public FlashBuildStepScriptlet(IScriptlet template,
                                   String sourceDir) {
        super(template)
        this.addMacroDefinitions([
                (token('SOURCE_DIR')): escape(sourceDir),
                (token('ARTIFACTS_DIR')): escape('result'),
                (token('ARTIFACTS_PATH')): escape('${WORKSPACE}/${ARTIFACTS_DIR}'),
            ])
    }
}
