package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobCronTriggerModel


class JobCronTriggerGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobCronTriggerModel m = (JobCronTriggerModel) model
        if (m.cronString) {
            entity.with {
                triggers {
                    cron(m.cronString)
                }
            }
        }

    }

}
