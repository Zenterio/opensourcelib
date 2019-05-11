package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.job.JobDefaultLoadBalancingModel

class JobDefaultLoadBalancingGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        JobDefaultLoadBalancingModel m = (JobDefaultLoadBalancingModel) model
        entity.configure { node ->
            (node / "properties" / "org.bstick12.jenkinsci.plugins.leastload.LeastLoadDisabledProperty" / "leastLoadDisabled").value = true
        }
    }
}
