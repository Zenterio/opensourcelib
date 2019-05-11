package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobScmTriggerModel


class JobScmTriggerGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobScmTriggerModel m = (JobScmTriggerModel) model
        if (m.cronString) {
            entity.with {
                triggers {
                    scm(m.cronString)
                }
            }
        }
    }

}
