package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobParameterModel


class JobParameterGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobParameterModel m = (JobParameterModel) model
        entity.with {
            parameters {
                stringParam(m.name, m.defaultValue, m.description)
            }
        }
    }
}
