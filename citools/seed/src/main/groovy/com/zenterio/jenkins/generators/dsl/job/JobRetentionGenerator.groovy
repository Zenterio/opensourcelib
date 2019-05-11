package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobRetentionModel


class JobRetentionGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobRetentionModel m = (JobRetentionModel) model

        entity.with {
            logRotator(m.policy.getDaysToKeep(),
                            m.policy.getNumToKeep(),
                            m.policy.getArtifactDaysToKeep(),
                            m.policy.getArtifactNumToKeep())
        }
    }
}
