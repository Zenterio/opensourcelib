package com.zenterio.jenkins.generators.console

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty
import com.zenterio.jenkins.models.IModel

import groovy.util.IndentPrinter
import groovy.util.logging.*


/**
 * Writes the model's class name and the property name if present.
 */
@Log
class SimpleTextGenerator implements IPropertyGenerator, IEntityGenerator {

    private OutputStream out

    public SimpleTextGenerator(OutputStream out) {
        this.out = out
    }

    @Override
    public void generate(ModelEntity model) {
        this.renderModel(model)

    }

    @Override
    public void generate(ModelProperty model, Object entity) {
        this.renderModel(model)
    }

    private void renderModel(IModel model) {
        String indent = '    ' * model.parents.size
        String name = this.getModelName(model)
        this.out.println("${indent}${model.class.name}(${name})")
    }

    private String getModelName(IModel model) {
        return (model.metaClass.hasProperty(model, "name")) ?
            model?.name : ''
    }

}
