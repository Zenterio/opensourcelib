package com.zenterio.jenkins.application

import com.zenterio.jenkins.dispatcher.LooseMatchDispatcher
import com.zenterio.jenkins.generators.shellscripts.PublishOverSSHScriptGenerator
import com.zenterio.jenkins.generators.shellscripts.ShellScriptGenerator
import com.zenterio.jenkins.models.job.JobPostBuildShellStepModel
import com.zenterio.jenkins.models.job.JobPublishOverSSHListModel
import com.zenterio.jenkins.models.job.JobShellStepModel
import groovy.util.logging.*


@Log
class XmlSeedShellscriptApplication extends XmlSeedBaseApplication {

    private String outputDirectory

    public XmlSeedShellscriptApplication(String scriptletsDirectory, String outputDirectory) {
        super (new LooseMatchDispatcher(true), scriptletsDirectory)
        this.outputDirectory = outputDirectory
        this.configureDispatcher()
    }

    private void configureDispatcher() {
        this.dispatcher.with {
            reg JobShellStepModel, new ShellScriptGenerator(this.outputDirectory)
            reg JobPostBuildShellStepModel, new ShellScriptGenerator(this.outputDirectory)
            reg JobPublishOverSSHListModel, new PublishOverSSHScriptGenerator(this.outputDirectory)
        }
    }

}
