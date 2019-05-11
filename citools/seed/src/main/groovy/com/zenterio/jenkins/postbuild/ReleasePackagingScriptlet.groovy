package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.JobIcon
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.escape
import static com.zenterio.jenkins.scriptlet.Token.groovyToken

/**
 * Generates a groovy scripts for annotate build chain jenkins-action.
 * Changes #ICON# to a list of repositories.
 * Changes #ANNOTATE_JOB_NAME# to the name of the jenkins job that performs the
 * build promotion. Allows for use of different annotation build jobs across projects.
 */
class ReleasePackagingScriptlet extends TemplateScriptlet {

    public ReleasePackagingScriptlet(IScriptlet template, String releasePackagingJobName,
            Boolean configurable, Origin origin) {
        super(template)

        this.addMacroDefinitions([
                (groovyToken("PROJECT")): escape(origin.project.name),
                (groovyToken("ORIGIN")): escape(origin.name),
                (groovyToken("RELEASE_PACKAGING_JOB_NAME")): escape(releasePackagingJobName),
                (groovyToken("ICON")): escape(JobIcon.PACKAGE.getPath()),
                (groovyToken("RELEASE_PACKAGING_CONFIGURABLE")): escape(configurable ? 'true' : 'false'),
            ])
    }
}
