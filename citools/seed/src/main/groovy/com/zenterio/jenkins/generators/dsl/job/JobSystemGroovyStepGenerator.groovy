package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobShellStepModel
import com.zenterio.jenkins.models.job.JobSystemGroovyScriptStepModel

class JobSystemGroovyStepGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobSystemGroovyScriptStepModel m = (JobSystemGroovyScriptStepModel) model;
        entity.with {
                steps {
                    systemGroovyCommand(m.script) {
                        sandbox(true)
                    }
                }
        }
    }
}
