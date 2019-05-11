package com.zenterio.jenkins.generators.dsl

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty

class DescriptionDisplayGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        if (model.description) {
            String currentDescription = entity.node.get('description')?.text()
            entity.with {
                description currentDescription + "\n" + model.description
            }
        }
    }
}
