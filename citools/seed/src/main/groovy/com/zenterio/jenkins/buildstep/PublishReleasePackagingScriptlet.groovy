package com.zenterio.jenkins.buildstep

import com.zenterio.jenkins.scriptlet.IScriptlet
import com.zenterio.jenkins.scriptlet.TemplateScriptlet

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

class PublishReleasePackagingScriptlet extends TemplateScriptlet {

    public PublishReleasePackagingScriptlet(IScriptlet template,
                                            String projectName,
                                            String originName,
                                            String jobName,
                                            String publishRoot,
                                            String contentDirectory
    ) {
        super(template)

        this.addMacroDefinitions(tokenizeAndEscape('PROJECT', projectName))
        this.addMacroDefinitions(tokenizeAndEscape('ORIGIN', originName))
        this.addMacroDefinitions(tokenizeAndEscape('JOB', jobName))
        this.addMacroDefinitions(tokenizeAndEscape('PUBLISH_ROOT', publishRoot))
        this.addMacroDefinitions(tokenizeAndEscape('CONTENT_DIR', contentDirectory))
    }
}
