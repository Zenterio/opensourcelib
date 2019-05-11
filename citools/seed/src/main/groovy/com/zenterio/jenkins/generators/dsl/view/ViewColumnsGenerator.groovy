package com.zenterio.jenkins.generators.dsl.view

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty


class ViewColumnsGenerator implements IPropertyGenerator {

    @Override
    public void generate(ModelProperty model, Object entity) {
        entity.with {
            columns {
                buildButton()
                status()
                customIcon()
                name()
                lastSuccess()
                lastFailure()
                lastDuration()
            }
        }
    }
}
