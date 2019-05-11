package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

class CoverityRunIfChangesScriptlet extends TemplateScriptlet {

    public CoverityRunIfChangesScriptlet(IScriptlet template, Repository[] repositories) {
        super(template)
        Map repoVarNameMap = [:]
        Map repoDefaultBranchMap = [:]
        repositories.each {Repository repo ->
            repoVarNameMap[repo.name] = repo.envName
            repoDefaultBranchMap[repo.name] = repo.branch
        }
        this.addMacroDefinitions([
                (groovyToken("REPO_VAR_NAME_MAP")): escape(repoVarNameMap.inspect()),
                (groovyToken("REPO_DEFAULT_BRANCH_MAP")): escape(repoDefaultBranchMap.inspect())

        ])

    }
}
