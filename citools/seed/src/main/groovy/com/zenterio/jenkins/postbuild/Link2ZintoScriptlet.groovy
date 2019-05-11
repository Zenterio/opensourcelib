package com.zenterio.jenkins.postbuild

import com.zenterio.jenkins.configuration.Repository
import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet
import com.zenterio.jenkins.JobIcon

/**
 * Injects the scriptlet template with needed information to generate
 * a groovy script to create links to Zinto test results on build
 * summary page.
 *
 * Currently no macros are needed.
 */
class Link2ZintoScriptlet extends TemplateScriptlet {

    public Link2ZintoScriptlet(IScriptlet template) {
        super(template)
    }
}
