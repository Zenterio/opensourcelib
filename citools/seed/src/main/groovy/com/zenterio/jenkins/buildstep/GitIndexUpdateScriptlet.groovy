package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.BuildEnv
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.token
import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

class GitIndexUpdateScriptlet extends TemplateScriptlet {

    public GitIndexUpdateScriptlet(String scriptletDirectory, Repository[] repositories, BuildEnv buildEnv) {
        super(new FileScriptlet("${scriptletDirectory}/buildsteps/git-index-update"))
        this.addMacroDefinitions([
            (token('REPOSITORY_DIRS')): repositories.collect({repo -> repo.directory}).join(' ')
        ])

        if (buildEnv?.getEnabled()) {
            this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT_PREFIX', "${buildEnv.prefix} "))
            this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT', "${buildEnv.prefix} exec "))
        } else {
            this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT_PREFIX', ""))
            this.addMacroDefinitions(tokenizeAndEscape('BUILD_ENVIRONMENT', ""))
        }
    }
    
}
