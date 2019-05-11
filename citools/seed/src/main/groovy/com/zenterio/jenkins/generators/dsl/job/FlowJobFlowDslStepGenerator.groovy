package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty


class FlowJobFlowDslStepGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        entity.with {
            buildFlow model.script
        }
    }

}
