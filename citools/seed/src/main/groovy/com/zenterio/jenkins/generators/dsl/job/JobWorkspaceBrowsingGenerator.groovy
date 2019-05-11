package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobWorkspaceBrowsingModel


class JobWorkspaceBrowsingGenerator implements IPropertyGenerator {
    @Override
    public void generate(ModelProperty model, Object entity) {
        JobWorkspaceBrowsingModel m = (JobWorkspaceBrowsingModel) model

        if (!m.enabled){
            entity.with {
                authorization {
                    permission('hudson.model.Item.Read:authenticated')
                    permission('hudson.model.Item.Build:authenticated')
                    permission('hudson.model.Item.Discover:authenticated')
                    permission('hudson.model.Item.Cancel:authenticated')
                    permission('hudson.model.Run.Update:authenticated')
                    permission('hudson.model.Item.Read:anonymous')
                    permission('hudson.model.Item.Discover:anonymous')
                    permissionAll('jenkins-administrators')
                    blocksInheritance()
                }
            }
        }
    }
}
