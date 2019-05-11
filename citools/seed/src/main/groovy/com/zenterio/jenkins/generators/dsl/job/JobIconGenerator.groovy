package com.zenterio.jenkins.generators.dsl.job

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty


class JobIconGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        entity.with {
            properties {
                customIcon(model.getIconFile())
            }
        }
    }
}
