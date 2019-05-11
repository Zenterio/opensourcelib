package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty


class JobDescriptionGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        entity.with {
            description model.description
        }
    }

}
