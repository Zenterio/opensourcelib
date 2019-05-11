package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.JobIcon
import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import static com.zenterio.jenkins.scriptlet.Token.escape


/**
 * Generates a groovy scripts for generating tag jenkins-action.
 * Changes #REPOSITORIES# to a list of repositories.
 * Changes #TAG-JOB-NAME# to the name of the jenkins job that performs the
 * tagging. Allows for use of different tagging jobs across projects.
 */
class TagBuildScriptlet extends TemplateScriptlet {

    public TagBuildScriptlet(IScriptlet template, Repository[] repositories, String tagJobName) {
        super(template)

        String repostring = repositories.toList().unique({a, b ->
            a.remote <=> b.remote
        }).collect({ Repository repo -> repo.toShortString() }).join(' ')

        this.addMacroDefinitions([
            "#REPOSITORIES#": escape(repostring),
            "#ICON#": escape(JobIcon.TAG.path),
            "#TAG-JOB-NAME#": escape(tagJobName)
            ])
    }
}
