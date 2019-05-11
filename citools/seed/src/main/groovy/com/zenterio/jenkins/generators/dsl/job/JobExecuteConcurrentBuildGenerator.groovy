package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobExecuteConcurrentBuildModel


class JobExecuteConcurrentBuildGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobExecuteConcurrentBuildModel m = (JobExecuteConcurrentBuildModel) model
        entity.with {
            concurrentBuild(m.getAllowConcurrentBuild())
            throttleConcurrentBuilds {
                maxPerNode(1)
                maxTotal(0)
            }
        }
    }
}
