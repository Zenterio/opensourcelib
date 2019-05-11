package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobParameterChoiceModel
import com.zenterio.jenkins.models.job.JobParameterModel


class JobParameterChoiceGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobParameterChoiceModel m = (JobParameterChoiceModel) model
        entity.with {
            parameters {
                choiceParam(m.name, m.values, m.description)
            }
        }
    }
}
