package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

@Canonical
@EqualsAndHashCode(callSuper=true, includeFields=true)
class VariableCollection extends ArrayList<Variable> {

    public VariableCollection clone() {
        return this.collect{ Variable var ->
            var.clone()
        } as VariableCollection
    }

    public void inheritFrom(VariableCollection other) {
        other.each { Variable var ->
            if (this.get(var.name) == null) {
                this.add(var.clone())
            }
        }
    }

    public String getValue(String variableName) {
        return this.get(variableName)?.value
    }

    public Variable get(String variableName) {
        return this.find({ it.name == variableName })
    }

    public static VariableCollection getTestData() {
        return [new Variable("var1", "value1"),
                new Variable("var2", "value2")] as VariableCollection
    }
}
