package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.ConsoleLogToWorkspaceBuildStepModel
import com.zenterio.jenkins.models.job.JobPostBuildShellStepModel
import com.zenterio.jenkins.models.job.JobPostBuildScriptWrapperModel

class JobPostBuildScriptWrapperGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobPostBuildScriptWrapperModel m = (JobPostBuildScriptWrapperModel) model
        entity.with {
            publishers {
                postBuildScripts {
                    steps {
                        m.getChildren().each { step ->
                            switch (step.class) {
                                case JobPostBuildShellStepModel:
                                    shell(step.script)
                                    break;
                                case ConsoleLogToWorkspaceBuildStepModel:
                                    consoleLogToWorkspace(step.fileName) {
                                        writeConsoleLog(true)
                                        blockOnAllOutput(true)
                                    }
                                    break
                                default:
                                    raise Exception("Unknown model (class=" + step.class.toString() + ")")
                                    break
                            }
                        }
                    }
                    onlyIfBuildSucceeds(!m.buildOnFailure)
                    onlyIfBuildFails(!m.buildOnSuccess)
                    markBuildUnstable(m.markUnstableOnFailure)
                }
            }
        }
    }
}
