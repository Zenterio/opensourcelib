package com.zenterio.jenkins.generators.dsl

import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelProperty


class HtmlCrumbDisplayGenerator implements IPropertyGenerator {

    public void generate(ModelProperty model, Object entity) {
        String currentDescription = entity.node.get('description')?.text()
        entity.with {
            description model.description +"\n" + currentDescription
        }
    }
}
