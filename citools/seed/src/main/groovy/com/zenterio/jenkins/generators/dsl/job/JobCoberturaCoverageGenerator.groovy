package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCoberturaCoverageModel

class JobCoberturaCoverageGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobCoberturaCoverageModel m = (JobCoberturaCoverageModel) model
        entity.with {
            publishers {
                cobertura(m.getPattern()) {
                    failNoReports(false)
                }
            }
        }
    }
}
