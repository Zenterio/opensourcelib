package com.zenterio.jenkins.models

import groovy.lang.Closure

import java.util.List


class ModelEntity extends BaseModel implements IPropertySelector {

    public Object entity
    protected IPropertySelector propertySelector

    public ModelEntity() {
        this.propertySelector = new PropertySelector(this)
        this.entity = null
    }

    @Override
    public IModel getProperty(Class cls, Boolean strict=true, Boolean recursive=true,
            Closure passFilter = {item, result -> true}) {
        return this.propertySelector.getProperty(cls, strict, recursive, passFilter)
    }

    @Override
    public IModel getProperty(Closure passFilter) {
        return this.propertySelector.getProperty(passFilter)
    }

    @Override
    public List<IModel> getProperties(Class cls, Boolean strict = true,
            Boolean recursive = false, Closure passFilter = {item, result -> true}) {
        return this.propertySelector.getProperties(cls, strict, recursive, passFilter)
    }

    @Override
    public List<IModel> getProperties(Closure passFilter) {
        return this.propertySelector.getProperties(passFilter)
    }

    @Override
    public IModel getParentProperty(Class cls, Boolean strict = true, Boolean recursive = false) {
        return this.propertySelector.getParentProperty(cls, strict, recursive)
    }

    @Override
    public List<IModel> getParentProperties(Class cls, Boolean strict = true, Boolean recursive = false) {
        return this.propertySelector.getParentProperties(cls, strict, recursive)
    }

    @Override
    public List<IModel> getParentsWithProperty(Class cls, Boolean strict = true, Boolean recursive = false) {
        return this.propertySelector.getParentsWithProperty(cls, strict, recursive)
    }
}
