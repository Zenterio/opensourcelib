package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.configuration.Resources
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty

class JobResourcesGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        Resources resources = model.resources
        entity.with {
            lockableResources(resources.name) {
                label(resources.label)
                resourceNumber(resources.quantity)
            }
        }
    }
}
