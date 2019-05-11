package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class ReleasePackagingCheckIfTargetExistsScriptlet extends TemplateScriptlet {

    public ReleasePackagingCheckIfTargetExistsScriptlet(IScriptlet template,
                                                        String publishRoot,
                                                        String publishPath
    ) {
        super(template)

        this.addMacroDefinitions([
                (groovyToken('PUBLISH_ROOT')): escape(publishRoot),
                (groovyToken('PUBLISH_PATH')): escape(publishPath),
        ])
    }
}
