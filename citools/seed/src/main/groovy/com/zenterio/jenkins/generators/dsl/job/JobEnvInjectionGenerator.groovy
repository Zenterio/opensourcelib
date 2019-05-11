package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobEnvInjectionModel


class JobEnvInjectionGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {

        JobEnvInjectionModel m = (JobEnvInjectionModel) model

        entity.with {
            environmentVariables {
                m.variables.each { key, value ->
                    env(key, value)
                }
                keepBuildVariables(true)
                keepSystemVariables(true)
            }
        }
    }
}
