package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobBlockOnDownStreamProjectsModel;

class JobBlockOnDownstreamProjectGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobBlockOnDownStreamProjectsModel m = (JobBlockOnDownStreamProjectsModel) model
        if (m.getBlock()) {
            entity.with {
                blockOnDownstreamProjects()
            }
        }
    }
}
