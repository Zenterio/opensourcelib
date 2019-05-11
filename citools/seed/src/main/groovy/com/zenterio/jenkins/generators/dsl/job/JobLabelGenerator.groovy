package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobLabelModel

class JobLabelGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobLabelModel m = (JobLabelModel) model

        if (m.configurable) {
            entity.with {
                parameters {
                    labelParam("node") {
                        defaultValue(m.label)
                        description("Label expression for the node to run on. Be careful to not change to an incompatible node.")
                    }
                }
            }
        } else {
            entity.with { label m.label }
        }
    }
}
