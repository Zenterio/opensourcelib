package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobParameterTextModel

class JobParameterTextGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobParameterTextModel m = (JobParameterTextModel) model
        entity.with {
            parameters {
                textParam(m.name, m.defaultValue, m.description)
            }
        }
    }
}
