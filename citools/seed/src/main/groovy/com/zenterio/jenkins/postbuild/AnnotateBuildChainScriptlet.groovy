package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon
import static com.zenterio.jenkins.scriptlet.Token.escape


/**
 * Generates a groovy scripts for annotate build chain jenkins-action.
 * Changes #ICON# to a list of repositories.
 * Changes #ANNOTATE_JOB_NAME# to the name of the jenkins job that performs the
 * build promotion. Allows for use of different annotation build jobs across projects.
 */
class AnnotateBuildChainScriptlet extends TemplateScriptlet {

    public AnnotateBuildChainScriptlet(IScriptlet template, String annotateBuildJobName) {
        super(template)

        this.addMacroDefinitions([
            "#ANNOTATE_JOB_NAME#": escape(annotateBuildJobName),
            "#ICON#": escape(JobIcon.ANNOTATE.path),
            ])
    }
}
