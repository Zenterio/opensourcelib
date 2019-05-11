package com.zenterio.jenkins.configuration.macroexpansion

import java.beans.PropertyDescriptor

import com.zenterio.jenkins.configuration.BaseConfig
import com.zenterio.jenkins.configuration.Project
import com.zenterio.jenkins.configuration.Origin
import com.zenterio.jenkins.configuration.Product
import com.zenterio.jenkins.configuration.IVariableContext
import com.zenterio.jenkins.configuration.Variable
import com.zenterio.jenkins.scriptlet.StringScriptlet

import static com.zenterio.jenkins.scriptlet.Token.tokenizeAndEscape

/**
 * The SeedContextTransform does a macro-expansion on strings, replacing
 * PROJECT, ORIGIN, PRODUCT with the respective names, based on the provided context.
 * It also takes the variable context of the last context object to perform
 * expansion of the variables defined.
 */
class SeedContextTransform extends StringScriptlet implements ITransform<BaseConfig> {

    SeedContextTransform() {
        super("")
    }

    /**
     * @param obj
     * @parma context
     */
    public Object transform(Object obj, List<BaseConfig> context) {
        if (obj == null) {
            return null
        }
        if (obj.class in String.class) {
            return this.transformString(obj, context)
        }
        return obj
    }

    /**
     * Transforms and returns the string (value) based on the provided context
     * @param value
     * @param context
     */
    protected String transformString(String value, List<BaseConfig> context) {
        if (value != null) {
            this.setRawContent(value)
            this.clearMacroDefinitions()
            Project p = this.getConfig(context, Project.class)
            Origin o = this.getConfig(context, Origin.class)
            Product prod = this.getConfig(context, Product.class)
            if (p != null) {
                this.addMacroDefinitions(tokenizeAndEscape('PROJECT', p.name))
                this.addMacroDefinitions(tokenizeAndEscape('project', p.name.toLowerCase()))
            }
            if (o != null) {
                this.addMacroDefinitions(tokenizeAndEscape('ORIGIN', o.name))
                this.addMacroDefinitions(tokenizeAndEscape('origin', o.name.toLowerCase()))
            }
            if (prod != null) {
                this.addMacroDefinitions(tokenizeAndEscape('PRODUCT', prod.name))
                this.addMacroDefinitions(tokenizeAndEscape('product', prod.name.toLowerCase()))
                this.addMacroDefinitions(tokenizeAndEscape('PRODUCT_ALT_NAME', prod.altName))
                this.addMacroDefinitions(tokenizeAndEscape('product_alt_name', prod.altName.toLowerCase()))
            }
            IVariableContext vc = this.getVariableContext(context)
            if (vc != null) {
                vc.variables.each { Variable variable ->
                    this.addMacroDefinitions(tokenizeAndEscape(variable.name, variable.value))
                }
            }

            value = this.getContent()
        }
        return value
    }

    /**
     * Returns the first class matching object in the context list.
     * The class must match exact.
     * @param context
     * @param cls
     */
    protected BaseConfig getConfig(List<BaseConfig> context, Class cls) {
        return context.find({ it.class == cls })
    }

    /**
     * Returns the last most present (last) object in the context list that
     * is a variable context (implements IVariableContext)
     * @param context
     */
    protected IVariableContext getVariableContext(List<BaseConfig> context) {
        return context.reverse().find({ (it instanceof IVariableContext) ? it : false })
    }

}
