package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobNeedWorkspaceModel


class JobNeedWorkspaceGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        JobNeedWorkspaceModel m = (JobNeedWorkspaceModel)model
        entity.configure { node ->
            (node / 'buildNeedsWorkspace').value = m.needed //TODO: supported in 1.42
        }
    }
}
