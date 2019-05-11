package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator

import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobPreScmBuildStepWrapperModel
import com.zenterio.jenkins.models.job.JobPreScmCopyArtifactsFromBuildNumberModel
import com.zenterio.jenkins.models.job.JobPreScmShellStepModel
import com.zenterio.jenkins.models.job.JobPreScmSystemGroovyScriptStepModel
import groovy.util.logging.Log

import static com.zenterio.jenkins.generators.dsl.job.JobCopyArtifactsFromBuildNumberGenerator.addCopyArtifacts

@Log
class JobPreScmBuildStepWrapperGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobPreScmBuildStepWrapperModel m = (JobPreScmBuildStepWrapperModel) model
        entity.with {
            wrappers {
                preScmSteps {
                    m.getChildren(JobPreScmCopyArtifactsFromBuildNumberModel).each { step ->
                        addCopyArtifacts(delegate.&steps, step)
                    }
                    steps {

                        m.getChildren(JobPreScmShellStepModel).each  { step ->
                            shell(step.script)
                        }

                        m.getChildren(JobPreScmSystemGroovyScriptStepModel).each { step ->
                            systemGroovyCommand(step.script) {
                                sandbox(true)
                            }
                        }
                    }
                    failOnError(m.failOnError)
                }
            }
        }
    }
}
