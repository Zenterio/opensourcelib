package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * Injects the scriptlet template with needed information to generate
 * a groovy script to create links to core dumps produced during a test run on
 * the build summary page.
 */
class Link2CoreDumpsScriptlet extends TemplateScriptlet {

    public Link2CoreDumpsScriptlet(IScriptlet template, String project, String coreDir) {
        super(template)

        this.addMacroDefinitions([
            (groovyToken("PROJECT")): escape(project),
            (groovyToken("CORE_DIR")): escape(coreDir)
        ])
    }
}
