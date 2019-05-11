package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.FileScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.token

class RepositoryJobParametersCheckScriptlet extends TemplateScriptlet {

    public RepositoryJobParametersCheckScriptlet(String scriptletDirectory, Repository[] repositories) {
        super(new FileScriptlet("${scriptletDirectory}/buildsteps/repo-job-parameters-check"))
        this.addMacroDefinitions([
            (token('REPOSITORY_PARAMETERS')): repositories.collect({repo -> repo.envName}).join(' ')
        ])
    }
    
}
